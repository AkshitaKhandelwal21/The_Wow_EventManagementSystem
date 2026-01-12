from django.urls import path
from . import views

urlpatterns = [
    path('new_event/', views.CreateEventView.as_view(), name='new_event'),
    path('org_dash/', views.OrganizerDashboardView.as_view(), name='org-dashboard'),
    path('user_dash/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('admin_dash/', views.AdmindashboardView.as_view(), name='admin-dashboard'),
    path('my_events/', views.MyEventsView.as_view(), name='my_events'),
    path('<int:pk>/', views.ViewEvent.as_view(), name='view_event'),
    path('edit_event/<int:pk>/', views.EditEventView.as_view(), name='edit_event'),
    path('delete_event/<int:pk>/', views.DeleteEventView.as_view(), name='delete_event'),
    path('all_events/', views.AllEventsView.as_view(), name='all_events'),
    path('<int:pk>/register/', views.UserRegisterView.as_view(), name='user-register'),
]   