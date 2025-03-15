from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Student
from django.utils.html import format_html
from django.utils import timezone

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Information'
    fk_name = 'user'
    readonly_fields = ('registered_at',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('mkid', 'email', 'first_name', 'last_name', 'register_no', 'recipt_no', 'is_enrolled', 'intercollege', 'is_staff')
    list_filter = ('recipt_no', 'is_enrolled', 'intercollege', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'register_no', 'mkid')
    ordering = ('-id',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('mkid',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'register_no', 'mobile_no', 'date_of_birth', 'password')
        }),
        ('MK ID', {
            'fields': ('mkid',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('recipt_no', 'intercollege', 'is_enrolled')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'register_no', 'mobile_no', 'date_of_birth',
                'password1', 'password2', 'recipt_no', 'intercollege', 'is_enrolled',
                'is_staff', 'is_superuser'
            )
        }),
    )

    inlines = [StudentInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_email', 'college_name', 'branch', 'dept', 'year_of_study', 'tshirt', 'get_registered_at', 'get_registration_status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'college_name', 'branch', 'dept')
    list_filter = ('branch', 'dept', 'year_of_study', 'tshirt', 'registered_at')
    readonly_fields = ('registered_at',)
    
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_name.short_description = 'Student Name'
    get_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

    def get_registered_at(self, obj):
        return obj.registered_at.strftime("%Y-%m-%d %H:%M:%S")
    get_registered_at.short_description = 'Registration Time'
    get_registered_at.admin_order_field = 'registered_at'

    def get_registration_status(self, obj):
        now = timezone.now()
        time_diff = now - obj.registered_at
        
        if time_diff.days < 1:  # Less than 24 hours
            return format_html('<span style="color: green;">New Registration</span>')
        elif time_diff.days < 7:  # Less than a week
            return format_html('<span style="color: blue;">Recent</span>')
        else:
            return format_html('<span style="color: gray;">Old</span>')
    get_registration_status.short_description = 'Status'

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Academic Information', {
            'fields': ('college_name', 'branch', 'dept', 'year_of_study')
        }),
        ('Additional Information', {
            'fields': ('tshirt', 'registered_at')
        }),
    )

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

admin.site.unregister(Group)