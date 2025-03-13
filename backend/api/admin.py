from django.contrib import admin
from .models import Cart, EventCategory, Event, Payment, Coordinator, RegisteredEvents, Winner

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('eventid', 'eventname', 'category', 'type', 'division', 'start_time', 'end_time', 'price')
    list_filter = ('category', 'type', 'division')
    search_fields = ('eventid', 'eventname', 'description')
    readonly_fields = ('eventid',)
    
    fieldsets = (
        ('Event Information', {
            'fields': ('eventname', 'description', 'category')
        }),
        ('Event Details', {
            'fields': ('type', 'division', 'start_time', 'end_time', 'price', 'participation_strength_setlimit')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('get_user_mkid', 'get_event_name', 'mindkraft', 'created_at')
    list_filter = ('mindkraft', 'created_at')
    search_fields = ('MKID__mkid', 'event__eventname')
    
    def get_user_mkid(self, obj):
        return obj.MKID.mkid
    get_user_mkid.short_description = 'MKID'
    
    def get_event_name(self, obj):
        return obj.event.eventname
    get_event_name.short_description = 'Event'

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ('CoordinateID', 'get_coordinator_name', 'get_user_mkid', 'get_event_name', 'created_at')
    list_filter = ('event__category', 'created_at')
    search_fields = ('get_coordinator_name', 'MKID__mkid', 'event__eventname')
    readonly_fields = ('CoordinateID',)
    
    def get_user_mkid(self, obj):
        return obj.MKID.mkid
    get_user_mkid.short_description = 'MKID'
    
    def get_event_name(self, obj):
        return obj.event.eventname
    get_event_name.short_description = 'Event'
    
    def get_coordinator_name(self, obj):
        return f'{obj.Student_coordinator_name} & {obj.Faculty_coordinator_name}'
    get_coordinator_name.short_description = 'Coordinator Name'


@admin.register(RegisteredEvents)
class RegisteredEventsAdmin(admin.ModelAdmin):
    list_display = ('MKID','event_name', 'payment_status', 'registered_at')
   # list_filter = ('payment_status', 'registered_at')
   # search_fields = ('MKID__mkid', 'event__eventname')
    
@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('get_event_name', 'get_user_mkid', 'position', 'prize_amount', 'created_at')
    list_filter = ('position', 'created_at', 'event__category')
    search_fields = ('MKID__mkid', 'event__eventname')
    
    fieldsets = (
        ('Winner Information', {
            'fields': ('event', 'MKID', 'position', 'prize_amount')
        }),
    )
    
    def get_user_mkid(self, obj):
        return obj.MKID.mkid
    get_user_mkid.short_description = 'MKID'
    
    def get_event_name(self, obj):
        return obj.event.eventname
    get_event_name.short_description = 'Event'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('get_user_mkid', 'get_event_count', 'added_at', 'updated_at')
    list_filter = ('added_at', 'updated_at')
    search_fields = ('MKID__mkid',)
    filter_horizontal = ('events',)  # This adds a nice widget for managing many-to-many relationships
    
    def get_user_mkid(self, obj):
        return obj.MKID.mkid
    get_user_mkid.short_description = 'MKID'
    
    def get_event_count(self, obj):
        return obj.events.count()
    get_event_count.short_description = 'Number of Events'
