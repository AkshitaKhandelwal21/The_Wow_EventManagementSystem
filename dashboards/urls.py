from django.urls import path
from . import views

urlpatterns = [
    path('new_event', views.CreateEventView.as_view(), name='signup'),
]