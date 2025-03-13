from rest_framework import serializers
from .models import *
from datetime import date, datetime

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['college_name', 'branch', 'dept', 'year_of_study', 'tshirt']

class UserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=False)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'register_no', 
            'mobile_no',
            'date_of_birth',
            'password',
            'mkid',
            'is_faculty',
            'intercollege',
            'is_enrolled',
            'student'
        ]
        read_only_fields = ['mkid']
    
    def to_representation(self, instance):
        # Convert date objects to string format
        ret = super().to_representation(instance)
        if 'date_of_birth' in ret and isinstance(ret['date_of_birth'], date):
            ret['date_of_birth'] = ret['date_of_birth'].strftime('%Y-%m-%d')
        return ret

    def create(self, validated_data):
        student_data = validated_data.pop('student', None)
        
        # Create user instance
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            register_no=validated_data['register_no'],
            mobile_no=validated_data['mobile_no'],
            password=validated_data['password'],
            date_of_birth=validated_data['date_of_birth'],
            is_faculty=validated_data.get('is_faculty', False),
            intercollege=validated_data.get('intercollege', False),
            is_enrolled=validated_data.get('is_enrolled', False)
        )

        # Create associated student if student data is provided
        if student_data and not user.is_faculty:
            Student.objects.create(user=user, **student_data)

        return user

    def update(self, instance, validated_data):
        student_data = validated_data.pop('student', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            if attr != 'password':
                setattr(instance, attr, value)
            else:
                instance.set_password(value)
        
        instance.save()

        # Update or create student information
        if student_data and not instance.is_faculty:
            student, created = Student.objects.get_or_create(user=instance)
            for attr, value in student_data.items():
                setattr(student, attr, value)
            student.save()

        return instance

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        if len(data['new_password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return data

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()