import logging
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, Event, RegisteredEvents
from .serializers import CartSerializer, DetailedRegisteredEventsSerializer, EventSerializer,RegisteredEventsSerializer
from rest_framework.permissions import IsAuthenticated
import json
from user.models import User, Student
from user.serializers import UserSerializer, StudentSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def list(self, request):
        """Get all events including coordinators"""
        queryset = self.get_queryset().prefetch_related('coordinators')
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Events retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def filter(self, request):
        """Filter events by category, type, or division"""
        category = request.query_params.get('category', None)
        type_ = request.query_params.get('type', None)
        division = request.query_params.get('division', None)
        eventid = request.query_params.get('eventid', None)
        
        queryset = self.queryset
        if category:
            queryset = queryset.filter(category__name=category)
        if type_:
            queryset = queryset.filter(type=type_)
        if division:
            queryset = queryset.filter(division=division)
        if eventid:
            queryset = queryset.filter(eventid=eventid)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Filtered events retrieved successfully',
            'data': serializer.data
        })
    
class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return cart items for the current user only
        return Cart.objects.filter(MKID=self.request.user)

    def list(self, request):
        """Get user's cart items"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Cart items retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request):
        """Add items to cart"""
        # Add current user's MKID to the data
        data = request.data.copy()
        data['MKID'] = request.user.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Items added to cart successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Failed to add items to cart',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove a specific event from the user's cart"""
        event_id = request.data.get('eventid')

        if not event_id:
            return Response({
                'status': 'error',
                'message': 'Event ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user's cart items
            cart_items = self.get_queryset()
            if not cart_items.exists():
                return Response({
                    'status': 'error',
                    'message': 'Cart not found for this user'
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if the event exists in the cart
            event_in_cart = cart_items.filter(events__eventid=event_id).exists()
            if not event_in_cart:
                return Response({
                    'status': 'error',
                    'message': 'Event not found in cart'
                }, status=status.HTTP_404_NOT_FOUND)

            # Remove the event from the cart
            cart_item = cart_items.first()
            event = Event.objects.get(eventid=event_id)
            cart_item.events.remove(event)

            return Response({
                'status': 'success',
                'message': f'Event {event_id} removed from cart successfully'
            }, status=status.HTTP_200_OK)
            

        except Event.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
class RegisteredEventsViewSet(viewsets.GenericViewSet):
    serializer_class = RegisteredEventsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return registered events for the current user only
        return RegisteredEvents.objects.filter(MKID=self.request.user)

    def list(self, request):
        """Get user's registered events"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Load event data from the JSON file
        with open('/home/dharshan/webprojects/mindkraft25/mindkraft_production/backend/updated_events(5).json', 'r') as file:
            events_data = json.load(file)

        # Calculate total amount
        total_amount = 0.0
        for registration in queryset:
            try:
                # Look up the corresponding Event based on event_name
                event = next((event for event in events_data if event['eventid'] == registration.event_name), None)
                if event:
                    total_amount += float(event['price'].replace('₹', ''))
            except (ValueError, KeyError):
                continue  # Skip if price conversion fails or event data is incomplete

        return Response({
            'status': 'success',
            'message': 'Registered events retrieved successfully',
            'data': {
                'registered_events': serializer.data,
                'total_events': len(serializer.data),
                'total_amount': total_amount
            }
        }, status=status.HTTP_200_OK)

  
from rest_framework.views import APIView
from .models import Event, RegisteredEvents


class RegisteredEventsAPIView(APIView):
    def post(self, request):
        user = request.user
        event_codes = request.data.get("event_name")

        if not event_codes or not isinstance(event_codes, list):
            return Response({"error": "Invalid event data. Expecting a list of event codes."}, status=400)

        registered_events = []
        failed_events = []

        for event_id in event_codes:
           
            # Update: Create the Registration with event_name instead of event
            try:
                RegisteredEvents.objects.create(MKID=user, event_name=event_id, payment_status=True)  # Use 'event_name'
                registered_events.append(event_id)
            except IntegrityError:
                failed_events.append(event_id)

        if not registered_events:
            return Response({"error": "No new events registered", "failed_events": failed_events}, status=400)

        return Response({
            "message": "Events registered successfully",
            "user_id": user.id,
            "registered_events": registered_events,
            "failed_events": failed_events
        })


class AllRegisteredEventsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def list(self, request):
        # Check if user is staff
        if not request.user.is_staff:
            return Response({
                'status': 'error',
                'message': 'You do not have permission to access this data'
            }, status=status.HTTP_403_FORBIDDEN)
        
        registered_events = RegisteredEvents.objects.all()
        
        if not registered_events.exists():
            return Response({
                'status': 'error',
                'message': 'No registered events found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Load event data from the JSON file
        with open('/home/dharshan/webprojects/mindkraft25/mindkraft_production/backend/updated_events(5).json', 'r') as file:
            events_data = json.load(file)
        
        detailed_registered_events = []
        for event in registered_events:
            user = User.objects.get(id=event.MKID.id)
            user_data = UserSerializer(user).data
            try:
                student = Student.objects.get(user=user)
                student_data = StudentSerializer(student).data
            except Student.DoesNotExist:
                student_data = None
            
            # Find the corresponding event details from the JSON data
            event_details = next((event_detail for event_detail in events_data if event_detail['eventid'] == event.event_name), None)
            
            event_data = DetailedRegisteredEventsSerializer(event).data
            event_data['user'] = user_data
            event_data['student'] = student_data
            event_data['event_details'] = event_details
            detailed_registered_events.append(event_data)
        
        return Response({
            'status': 'success',
            'message': 'All registered events retrieved successfully',
            'data': detailed_registered_events
        }, status=status.HTTP_200_OK)