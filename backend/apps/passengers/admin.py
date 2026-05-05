from django.contrib import admin
from .models import Passenger

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'passenger_type', 'owner', 'is_active', 'created_at']
    list_filter = ['passenger_type', 'gender', 'relationship', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'owner__email', 'id_number']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'dob', 'gender', 'nationality')
        }),
        ('Travel Details', {
            'fields': ('passenger_type', 'relationship', 'id_type', 'id_number')
        }),
        ('Ownership & Status', {
            'fields': ('owner', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
