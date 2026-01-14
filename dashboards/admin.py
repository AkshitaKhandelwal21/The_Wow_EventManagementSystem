from django.contrib import admin

from dashboards.models import Event, EventRegistration


class EventAdmin(admin.ModelAdmin):
    class Meta:
        model = Event

    list_display = [
        'title', 'description', 'user', 'category', 'image'
    ]
    fieldsets = [
        ("Event Info", {'fields': [
            'title', 'description', 'category', 'venue', 'image'
        ]}),
        ("Events Metadata", {'fields': [
            'date', 'time', 'address', 'duration', 'seats'
        ]}),
        ("Creation Info", {'fields': [
            'user', 'created_at', 'updated_at'
        ]})
    ]

# Register your models here.
admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration)