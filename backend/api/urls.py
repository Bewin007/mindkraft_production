from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AllRegisteredEventsViewSet, CartViewSet, EventViewSet, RegisteredEventsViewSet, RegisteredEventsAPIView

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'registered-events', RegisteredEventsViewSet, basename='registered-events')
router.register(r'all-registered-events', AllRegisteredEventsViewSet, basename='all-registered-events')

# URL patterns for the API app
urlpatterns = [
    path('', include(router.urls)),  # Include the registered viewsets
    path('test/', RegisteredEventsAPIView.as_view()),  # Custom path for RegisteredEventsAPIView
]