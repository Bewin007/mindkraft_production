import json
from rest_framework import serializers
from .models import Event, Winner, EventCategory, Payment, Coordinator, RegisteredEvents, Cart
from user.models import User, Student

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name']

class WinnerSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.eventname', read_only=True)
    winner_mkid = serializers.CharField(source='MKID.mkid', read_only=True)

    class Meta:
        model = Winner
        fields = ['id', 'event', 'event_name', 'MKID', 'winner_mkid', 
                 'position', 'prize_amount', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    user_mkid = serializers.CharField(source='MKID.mkid', read_only=True)
    event_name = serializers.CharField(source='event.eventname', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'MKID', 'user_mkid', 'mindkraft', 
                 'event', 'event_name', 'created_at']

class CoordinatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields = [
            'Student_coordinator_name',
            'Student_coordinator_mobile_no',
            'Faculty_coordinator_name',
            'Faculty_coordinator_mobile_no' ,
        ]

class EventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    coordinators = CoordinatorSerializer(many=True, read_only=True) 

    class Meta:
        model = Event
        fields = [
            'eventid', 'eventname', 'description', 'type',
            'category', 'category_name', 'division',
            'start_time', 'end_time', 'price',
            'participation_strength_setlimit', 'coordinators'
        ]

class RegisteredEventsSerializer(serializers.ModelSerializer):
    user_mkid = serializers.CharField(source='MKID.mkid', read_only=True)  # Get mkid from the related User model
    event_details = serializers.SerializerMethodField()  # Get event details from the JSON data

    class Meta:
        model = RegisteredEvents
        fields = ['MKID', 'user_mkid', 'event_name', 'payment_status', 'registered_at', 'updated_at', 'event_details']

    def get_event_details(self, obj):
        # Load event data from the JSON file
        with open('/home/dharshan/webprojects/mindkraft25/mindkraft_production/backend/updated_events(5).json', 'r') as file:
            events_data = json.load(file)

        # Find the event details based on the event_name (which is actually the eventid)
        event_details = next((event for event in events_data if event['eventid'] == obj.event_name), None)
        return event_details

class CartSerializer(serializers.ModelSerializer):
    user_mkid = serializers.CharField(source='MKID.mkid', read_only=True)
    events_detail = EventSerializer(source='events', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'MKID', 'user_mkid', 'events', 
                 'events_detail', 'added_at', 'updated_at']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'register_no', 
            'mobile_no', 'mkid', 'date_of_birth', 'recipt_no', 
            'intercollege', 'is_enrolled'
        ]

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'college_name', 'branch', 'dept', 
            'year_of_study', 'tshirt', 'registered_at'
        ]

class DetailedRegisteredEventsSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='MKID', read_only=True)
    student = serializers.SerializerMethodField()

    class Meta:
        model = RegisteredEvents
        fields = [
            'id', 'event_name', 'payment_status', 
            'registered_at', 'updated_at', 'user', 'student'
        ]

    def get_student(self, obj):
        try:
            student = Student.objects.get(user=obj.MKID)
            return StudentSerializer(student).data
        except Student.DoesNotExist:
            return None