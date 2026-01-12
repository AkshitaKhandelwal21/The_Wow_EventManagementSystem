from django.urls import path
from . import views

urlpatterns = [
    path('new_event/', views.CreateEventView.as_view(), name='new_event'),
    path('org_dash/', views.OrganizerDashboardView.as_view(), name='org-dashboard'),
    path('my_events/', views.MyEventsView.as_view(), name='my_events'),
    path('events/<int:id>/', views.ViewEvent.as_view(), name='view_event'),
]