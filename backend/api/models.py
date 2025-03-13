from datetime import datetime
from django.db import models
from user.models import User 

class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'events_categories'
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'

class Event(models.Model):
    eventid = models.CharField(max_length=10, primary_key=True, editable=False, default='')
    eventname = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, help_text="Detailed description of the event")
    type = models.CharField(max_length=100)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    division = models.CharField(max_length=100)
    start_time = models.DateTimeField(default=datetime(2025, 3, 21, 9, 0))  # 21st March 2025, 9 AM
    end_time = models.DateTimeField(default=datetime(2025, 3, 22, 18, 0))   # 22nd March 2025, 6 PM
    price = models.DecimalField(max_digits=10, decimal_places=2)
    participation_strength_setlimit = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.eventid:
            last_event = Event.objects.all().order_by('eventid').last()
            if not last_event:
                self.eventid = 'MK25E0001'
            else:
                last_event_id = last_event.eventid
                event_int = int(last_event_id[5:])
                new_event_int = event_int + 1
                self.eventid = f'MK25E{new_event_int:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.eventid} - {self.eventname}"

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

class Winner(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, primary_key=True, db_column='eventid')
    coordinatorid = models.IntegerField(default='')
    first_place = models.IntegerField()
    second_place = models.IntegerField()
    third_place = models.IntegerField()

    def __str__(self):
        return f"Winners for {self.event.eventname}"

    class Meta:
        db_table = 'winning'
        verbose_name = 'Winner'
        verbose_name_plural = 'Winners'

class Payment(models.Model):
    MKID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    mindkraft = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'

class Coordinator(models.Model):
    MKID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coordinator_roles')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='coordinators')
    CoordinateID = models.AutoField(primary_key=True)
    Student_coordinator_name = models.CharField(max_length=255,default='')
    Student_coordinator_mobile_no = models.CharField(max_length=20,default='')
    Student_coordinator_email = models.EmailField(max_length=255, unique=True,default='')
    Faculty_coordinator_name = models.CharField(max_length=255,default='')
    Faculty_coordinator_mobile_no = models.CharField(max_length=20,default='')
    Faculty_coordinator_email = models.EmailField(max_length=255, unique=True,default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coordinator'
        unique_together = ['MKID', 'event']

class RegisteredEvents(models.Model):
    MKID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_events')
    event_name = models.CharField(max_length=255, default='')  # Store the event name instead of a ForeignKey
    payment_status = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'registered_events'
        unique_together = ['MKID', 'event_name']  # Ensure 'event_name' is included here


class Winner(models.Model):
    id = models.AutoField(primary_key=True)  # Add explicit id field
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='winners')
    MKID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wins', default=1)
    position = models.IntegerField()
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'winning'
        unique_together = ['event', 'position']

    def __str__(self):
        return f"{self.MKID.mkid} - {self.event.eventname} - Position {self.position}"
    
class Cart(models.Model):
    MKID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    events = models.ManyToManyField(Event, related_name='in_carts')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart for {self.MKID.mkid}"
