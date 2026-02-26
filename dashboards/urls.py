from django.urls import path
from . import views

urlpatterns = [
    path('user_dash/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('all_events/', views.AllEventsView.as_view(), name='all_events'),
    path('<int:pk>/register/', views.UserRegisterView.as_view(), name='user-register'),
    path("payment-success/<int:pk>/", views.payment_success, name="payment-success"),
    path('payment-cancel/<int:pk>/', views.payment_cancel, name='payment-cancel'),
    path('<int:pk>/summary/', views.PaymentSummaryView.as_view(), name='summary'),
    path('checkout_session/', views.CreateCheckoutSession.as_view(), name='checkout'),
    path('reg_events/', views.MyRegisteredEventsView.as_view(), name='reg-events'),
    path("ticket/<int:pk>/", views.TicketQRView.as_view(), name="ticket-qr"),
    path("qr/<uuid:token>/", views.QRImageView.as_view(), name="qr-image"),
    path("verify-ticket/<uuid:token>/", views.VerifyTicketView.as_view(), name="verify-ticket"),
    path('<int:pk>/', views.ViewEvent.as_view(), name='view_event'),

    path('new_event/', views.CreateEventView.as_view(), name='new_event'),
    path('org_dash/', views.OrganizerDashboardView.as_view(), name='org-dashboard'),
    path('my_events/', views.MyEventsView.as_view(), name='my_events'),   
    path('edit_event/<int:pk>/', views.EditEventView.as_view(), name='edit_event'),
    path('delete_event/<int:pk>/', views.DeleteEventView.as_view(), name='delete_event'),
    path('guests/<int:pk>', views.GuestsListView.as_view(), name='guests'),
    path('event/export-guests/', views.ExportGuestsCSVView.as_view(), name='export_guests_csv'),
    path('<int:id>/followup/', views.FollowUpMailView.as_view(), name='followup'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('revenue/', views.RevenueView.as_view(), name='revenue'),

    path('admin_dash/', views.AdmindashboardView.as_view(), name='admin-dashboard'),
]