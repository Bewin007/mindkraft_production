from django.shortcuts import render
from django.utils import timezone
from tokenize import TokenError
from datetime import datetime, date
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import logging
import json
import redis
import random
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction

from .models import User
from .serializers import ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer
from api.models import Cart, Event

# Configure logging
logger = logging.getLogger(__name__)

# Create Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
    port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
    db=settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0,
    password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
    decode_responses=True  # Automatically decode responses to strings
)

# Helper functions for OTP
def generate_otp():
    """Generate a 6-digit OTP"""
    otp = str(random.randint(100000, 999999))
    logger.info(f"Generated new OTP: {otp[:2]}****")  # Log only first 2 digits for security
    return otp

def store_otp_securely(email, otp, purpose='registration'):
    """Store OTP in Redis with expiration"""
    # Create a unique key for this email and purpose
    key = f"{purpose}_{email}"
    
    # Hash the OTP using Django's password hasher (includes salt automatically)
    hashed_otp = make_password(otp)
    
    # Store hashed OTP with 10 minute expiration
    redis_client.setex(key, 600, hashed_otp)  # 600 seconds = 10 minutes
    
    logger.info(f"Stored OTP for {email} (purpose: {purpose}), expires in 10 minutes")
    logger.debug(f"Redis key: {key}")

def verify_otp(email, provided_otp, purpose='registration'):
    """Verify the provided OTP against the stored hash in Redis"""
    key = f"{purpose}_{email}"
    
    # Get the hashed OTP from Redis
    hashed_otp = redis_client.get(key)
    
    # If no hashed OTP found or it's expired
    if not hashed_otp:
        logger.warning(f"OTP verification failed for {email}: OTP not found or expired")
        return False
    
    # Verify the provided OTP against the stored hash
    is_valid = check_password(provided_otp, hashed_otp)
    
    if is_valid:
        logger.info(f"OTP verified successfully for {email}")
    else:
        logger.warning(f"Invalid OTP provided for {email}")
    
    return is_valid

def clear_otp(email, purpose='registration'):
    """Delete OTP from Redis"""
    key = f"{purpose}_{email}"
    redis_client.delete(key)
    logger.info(f"Cleared OTP for {email} (purpose: {purpose})")

def store_registration_data(email, data):
    """Store registration data in Redis temporarily"""
    key = f"reg_data_{email}"
    
    # Convert objects for JSON serialization
    serialized_data = data.copy()
    
    # Convert date to string for storage
    if isinstance(serialized_data.get('date_of_birth'), date):
        serialized_data['date_of_birth'] = serialized_data['date_of_birth'].strftime('%Y-%m-%d')
    
    # Convert to JSON string
    json_data = json.dumps(serialized_data)
    
    # Store in Redis with 10 minute expiration
    redis_client.setex(key, 600, json_data)
    
    logger.info(f"Stored registration data for {email}, expires in 10 minutes")
    logger.debug(f"Registration data: {serialized_data}")

def get_registration_data(email):
    """Retrieve registration data from Redis"""
    key = f"reg_data_{email}"
    json_data = redis_client.get(key)
    
    if not json_data:
        logger.warning(f"Registration data not found for {email}")
        return None
    
    data = json.loads(json_data)
    
    # Convert string back to date
    if data and 'date_of_birth' in data:
        data['date_of_birth'] = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    
    logger.info(f"Retrieved registration data for {email}")
    logger.debug(f"Registration data: {data}")
    
    return data

def clear_registration_data(email):
    """Delete registration data from Redis"""
    key = f"reg_data_{email}"
    redis_client.delete(key)
    logger.info(f"Cleared registration data for {email}")

class VerifyOTPView(APIView):
    def post(self, request):
        provided_otp = request.data.get('otp')
        email = request.data.get('email')
        
        logger.info(f"OTP verification request for email: {email}")
        logger.debug(f"OTP provided: {provided_otp[:2]}****" if provided_otp else "No OTP provided")
        
        if not email:
            logger.warning("OTP verification failed: email not provided")
            return Response({
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the OTP
        if verify_otp(email, provided_otp):
            # Get registration data from Redis
            registration_data = get_registration_data(email)
            
            if not registration_data:
                logger.warning(f"Registration data expired for {email}")
                return Response({
                    'message': 'Registration data expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user with stored registration data
            serializer = UserSerializer(data=registration_data)
            if serializer.is_valid():
                # Use a database transaction to ensure both user creation and cart creation succeed or fail together
                try:
                    with transaction.atomic():
                        # Save the user
                        user = serializer.save()
                        
                        # Get or create the mindkraft event with all required fields
                        try:
                            mindkraft_event = Event.objects.get(eventname="mindkraft")
                        except Event.DoesNotExist:
                            # Get tomorrow's date for start date and day after for end date
                            start_date = timezone.now() + timezone.timedelta(days=1)
                            end_date = timezone.now() + timezone.timedelta(days=2)
                            
                            # Create with all fields that might be required
                            mindkraft_event = Event.objects.create(
                                eventname="mindkraft",
                                price=250,
                                description='Mindkraft 25 Registration',
                                # start_date=start_date,
                                # end_date=end_date,
                                participation_strength_setlimit='0',  # Set a default value
                            )
                        
                        # Create a cart for the user
                        cart = Cart.objects.create(MKID=user)
                        
                        # Add the mindkraft event to the cart
                        cart.events.add(mindkraft_event)
                        
                        logger.info(f"Added default mindkraft event to cart for user {email}")
                        
                        # Clear OTP and registration data from Redis
                        clear_otp(email)
                        clear_registration_data(email)
                        
                        logger.info(f"Registration successful for {email}")
                        
                        return Response({
                            'message': 'Registration successful',
                            'user': serializer.data
                        }, status=status.HTTP_201_CREATED)
                
                except Exception as e:
                    # If anything fails, the transaction will be rolled back
                    logger.error(f"Registration failed: Error adding default event to cart: {str(e)}")
                    return Response({
                        'message': 'Registration failed: Could not add default event to cart',
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.warning(f"User validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning(f"Invalid OTP provided for {email}")
        return Response({
            'message': 'Invalid OTP'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
    permission_classes=[AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        user = authenticate(request, email=email, password=password)
        data = User.objects.filter(email=email).first()
        if user is not None and data is not None:
            refresh = RefreshToken.for_user(user)
            
            # Get student information from the user model with correct field names
            first_name = getattr(data, 'first_name', '')
            last_name = getattr(data, 'last_name', '')
            name = f"{first_name} {last_name}".strip()
            register_no = getattr(data, 'register_no', '')
            mobile_no = getattr(data, 'mobile_no', '')
            mkid = getattr(data, 'mkid', '')
            intercollege = getattr(data, 'intercollege', False)
            is_faculty = getattr(data, 'is_faculty', False)
            
            # Include user information in custom_data
            custom_data = {
                'email': data.email,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': name,
                'register_no': register_no,
                'mobile_no': mobile_no,
                'mkid': mkid,
                'intercollege': intercollege,
                'is_faculty': is_faculty
            }
            
            refresh['custom_data'] = custom_data
            refresh.access_token.payload['custom_data'] = custom_data

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': data.email,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': name,
                'register_no': register_no,
                'mobile_no': mobile_no,
                'mkid': mkid,
                'intercollege': intercollege,
                'is_faculty': is_faculty
            }
            
            # If user is a student, try to get additional student details
            try:
                if not is_faculty and hasattr(data, 'student'):
                    student = data.student
                    student_data = {
                        'college_name': student.college_name,
                        'branch': student.branch,
                        'dept': student.dept,
                        'year_of_study': student.year_of_study,
                        'tshirt': student.tshirt
                    }
                    response_data['student_details'] = student_data
                    custom_data['student_details'] = student_data
                    refresh['custom_data'] = custom_data
                    refresh.access_token.payload['custom_data'] = custom_data
            except Exception as e:
                logger.warning(f"Could not retrieve student details: {str(e)}")
            
            logger.info(f"User {email} logged in successfully")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed login attempt for {email}")
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            user_email = request.user.email
            logger.info(f"Logout attempt for user: {user_email}")
            
            if not refresh_token:
                logger.warning(f"Logout failed - no refresh token provided for {user_email}")
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"User {user_email} logged out successfully")
                return Response(
                    {'message': 'Successfully logged out'}, 
                    status=status.HTTP_200_OK
                )
            except TokenError as e:
                logger.warning(f"Logout failed - invalid token for {user_email}: {str(e)}")
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UserRegistrationView(APIView):
    def send_otp_email(self, email, otp):
        subject = 'Email Verification OTP for Mindkraft 25'
        message = f'Your OTP for email verification is: {otp}'
        message += f'\nThis OTP will expire in 10 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        logger.info(f"Sending verification OTP email to {email}")
        send_mail(subject, message, from_email, recipient_list)
    
    def post(self, request):
        logger.info("Registration request received")
        logger.debug(f"Registration data: {request.data}")
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Generate OTP
            otp = generate_otp()
            
            # Get validated data
            registration_data = serializer.validated_data
            email = registration_data['email']
            
            # Store hashed OTP and registration data in Redis
            store_otp_securely(email, otp)
            store_registration_data(email, registration_data)
            
            # Send OTP via email
            self.send_otp_email(email, otp)
            
            logger.info(f"Registration initiated for {email}, OTP sent")
            
            return Response({
                'message': 'OTP sent to your email. It will expire in 10 minutes.',
                'email': email
            }, status=status.HTTP_200_OK)
        
        logger.warning(f"Invalid registration data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class VerifyOTPView(APIView):
#     def post(self, request):
#         provided_otp = request.data.get('otp')
#         email = request.data.get('email')
        
#         logger.info(f"OTP verification request for email: {email}")
#         logger.debug(f"OTP provided: {provided_otp[:2]}****" if provided_otp else "No OTP provided")
        
#         if not email:
#             logger.warning("OTP verification failed: email not provided")
#             return Response({
#                 'message': 'Email is required'
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         # Verify the OTP
#         if verify_otp(email, provided_otp):
#             # Get registration data from Redis
#             registration_data = get_registration_data(email)
            
#             if not registration_data:
#                 logger.warning(f"Registration data expired for {email}")
#                 return Response({
#                     'message': 'Registration data expired'
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             # Create user with stored registration data
#             serializer = UserSerializer(data=registration_data)
#             if serializer.is_valid():
#                 user = serializer.save()
                
#                 # Clear OTP and registration data from Redis
#                 clear_otp(email)
#                 clear_registration_data(email)
                
#                 # Add default mindkraft event to cart
#                 try:
#                     # Get or create the mindkraft event (assuming it exists in the database)
#                     mindkraft_event, created = Event.objects.get_or_create(
#                         eventname="mindkraft", 
#                         defaults={'price': 250, 'description': 'Mindkraft 25 Registration'}
#                     )
                    
#                     # Create a cart for the user
#                     cart = Cart.objects.create(MKID=user)
                    
#                     # Add the mindkraft event to the cart
#                     cart.events.add(mindkraft_event)
                    
#                     logger.info(f"Added default mindkraft event to cart for user {email}")
#                 except Exception as e:
#                     logger.error(f"Error adding default event to cart: {str(e)}")
                
#                 logger.info(f"Registration successful for {email}")
                
#                 return Response({
#                     'message': 'Registration successful',
#                     'user': serializer.data
#                 }, status=status.HTTP_201_CREATED)
            
#             logger.warning(f"User validation failed: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         logger.warning(f"Invalid OTP provided for {email}")
#         return Response({
#             'message': 'Invalid OTP'
#         }, status=status.HTTP_400_BAD_REQUEST)

class InitiateForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def send_reset_otp(self, email, otp):
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}\nThis OTP will expire in 10 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        logger.info(f"Sending password reset OTP email to {email}")
        send_mail(subject, message, from_email, recipient_list)
    
    def post(self, request):
        logger.info("Password reset request received")
        
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            logger.info(f"Processing password reset for email: {email}")
            
            # Check if user exists
            try:
                user = User.objects.get(email=email)
                
                # Generate and store hashed OTP in Redis
                otp = generate_otp()
                store_otp_securely(email, otp, purpose='reset_password')
                
                # Send OTP via email
                self.send_reset_otp(email, otp)
                logger.info(f"Password reset OTP sent to {email}")
            except User.DoesNotExist:
                # Don't reveal if user exists or not for security
                logger.info(f"Password reset requested for non-existent user: {email}")
                pass
            
            return Response({
                'message': 'If a user with this email exists, they will receive a password reset OTP.'
            }, status=status.HTTP_200_OK)
            
        logger.warning(f"Invalid password reset data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordWithOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        logger.info("Password reset verification request received")
        
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            provided_otp = serializer.validated_data['otp']
            
            logger.info(f"Verifying password reset OTP for {email}")
            logger.debug(f"OTP provided: {provided_otp[:2]}****" if provided_otp else "No OTP provided")
            
            # Verify the OTP
            if verify_otp(email, provided_otp, purpose='reset_password'):
                try:
                    user = User.objects.get(email=email)
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    # Clear OTP from Redis
                    clear_otp(email, purpose='reset_password')
                    
                    logger.info(f"Password successfully reset for {email}")
                    
                    return Response({
                        'message': 'Password successfully reset'
                    }, status=status.HTTP_200_OK)
                    
                except User.DoesNotExist:
                    logger.warning(f"Password reset failed: User not found - {email}")
                    return Response({
                        'message': 'User not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.warning(f"Password reset failed: Invalid OTP for {email}")
                return Response({
                    'message': 'Invalid or expired OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        logger.warning(f"Invalid password reset verification data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)