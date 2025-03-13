from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, Event, RegisteredEvents
from .serializers import CartSerializer, EventSerializer,RegisteredEventsSerializer
from rest_framework.permissions import IsAuthenticated

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

        # Calculate total amount
        total_amount = 0.0
        for registration in queryset:
            try:
                # Look up the corresponding Event based on event_name
                event = Event.objects.get(eventname=registration.event_name)
                total_amount += float(event.price)
            except Event.DoesNotExist:
                continue  # Skip if Event doesn't exist for the given event_name

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

