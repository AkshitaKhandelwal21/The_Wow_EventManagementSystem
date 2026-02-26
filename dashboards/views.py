from io import BytesIO
from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import qrcode
from The_Wow import settings
from dashboards.forms import CreateEventForm, EditEventForm
from dashboards.services import get_monthly_registration_data, get_top_events
from dashboards.tasks import follow_email_to_guests
from .models import Event, EventRegistration
from django.utils.timezone import now
import csv
from django.db.models import Count, Sum
from .mixin import EventFilterMixin
import stripe
import datetime
from django.utils import timezone

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


# ****************************** User Views ***********************************

class UserDashboardView(TemplateView):
    template_name = "user/user_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registrations = EventRegistration.objects.filter(user=self.request.user).select_related(
            'event').order_by('event__date')[:3]
        context['activities'] = registrations
        return context
    

class ViewEvent(LoginRequiredMixin, TemplateView):
    template_name = 'organizer/view_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs['pk']
        event = get_object_or_404(
            Event.objects.select_related('user'), id=event_id
        )
        context['event'] = event
        registration = EventRegistration.objects.filter(
            user=self.request.user, event=event
        ).first()
        context['registration'] = registration
        context['is_reg'] = registration is not None

        guests = EventRegistration.objects.filter(event=event).count()
        context['guests'] = guests
        today = now().date()
        context['similar_events'] = Event.objects.filter(
            category = event.category, date__gte=today
        ).exclude(id=event.id)[:3]
        return context
    

class AllEventsView(EventFilterMixin, TemplateView):
    template_name = 'user/all_events.html'

    DATE_FILTER_CHOICES = [
    ("", "Any Date"),
    ("today", "Today"),
    ("tomorrow", "Tomorrow"),
    ("this-week", "This Week"),
    ("this-month", "This Month"),
    # ("custom", "Custom Date Range"),
    ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.annotate(guests_count=Count('registrations'))
        events = self.filter_queryset(events)
        context['date_choices'] = self.DATE_FILTER_CHOICES
        context['events'] = events
        return context
    

class RevenueView(TemplateView):
    template_name = 'organizer/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_revenue'] = EventRegistration.objects.filter(
            event__user = self.request.user, payment_status = True, event_price__isnull = False
        ).aaggregate(total_revenue=Sum())
    

class UserRegisterView(TemplateView):
    template_name = 'organizer/view_event.html'

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])

        if event.price:
            return redirect('summary', pk=event.pk)
        
        register, created = EventRegistration.objects.get_or_create(
            user=request.user, event=event
        )
        if created:
            return redirect('ticket-qr', pk=register.pk)

        return redirect('view_event', pk=event.pk) 


class PaymentSummaryView(TemplateView):
    template_name = 'user/payment_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['user'] = self.request.user
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        context['pf'] = (event.price) / 100
        context['gst'] = ((event.price) * 18) / 100
        context['event'] = event
        context['total'] = event.price + ((event.price) / 100) + (((event.price) * 18) / 100)
        return context


class CreateCheckoutSession(View):
    def post(self, request, *args, **kwargs):
        host = self.request.get_host()
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, pk=event_id)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[ 
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": event.title,
                        },
                        "unit_amount": int(event.price * 100),
                    },
                    "quantity": 1,
                }
                ],
                mode='payment',
                success_url=f"http://{host}/event/payment-success/{event.id}/",
                cancel_url=f"http://{host}/event/{event.id}/summary/",
            )
        except Exception as e:
            return HttpResponse(f"Stripe Error: {str(e)}")

        return redirect(checkout_session.url, code=303)
    
def payment_success(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.seats > 0:
        register, created = EventRegistration.objects.get_or_create(
            user=request.user, event=event
        )
        if created:
            event.seats -= 1
            event.save(update_fields=['seats'])

            return redirect('ticket-qr', pk=register.pk)
        
    return redirect('view_event', pk=event.pk) 

def payment_cancel(request):
    context = {
        'payment_status': 'cancel'
    }
    return render(request, 'user/success.html', context)


class MyRegisteredEventsView(TemplateView):
    template_name = 'user/registered_events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registrations = EventRegistration.objects.select_related('event').filter(
            user=self.request.user
        )
        context['upcoming'] = registrations.filter(event__date__gte=now().date(), user=self.request.user).order_by('event__date')
        context['past'] = registrations.filter(event__date__lt=now().date(), user=self.request.user)
        return context
    

class QRImageView(View):

    def get(self, request, *args, **kwargs):
        token = self.kwargs['token']

        registration = get_object_or_404(
            EventRegistration,
            qr_token=token,
            user=request.user
        )

        qr_data = request.build_absolute_uri(
            f"/event/verify-ticket/{registration.qr_token}/"
        )

        img = qrcode.make(qr_data)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')


class TicketQRView(TemplateView):
    template_name = 'user/ticket_qr.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = get_object_or_404(EventRegistration, pk=self.kwargs['pk'], user=self.request.user)
        context['registration'] = registration
        return context
    

class VerifyTicketView(View):

    def get(self, request, *args, **kwargs):
        qr_token = self.kwargs['token']
        registration = get_object_or_404(EventRegistration, qr_token=qr_token)
        if registration.event.date < now().date():
            return HttpResponse("This ticket is for an event that has already passed.")
        return HttpResponse(f"Ticket for {registration.event.title} is valid for user {registration.user.username}")
    


#  ****************************** Organizer Views ***********************************
class OrganizerDashboardView(TemplateView):
    template_name = 'organizer/organizer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events'] = Event.objects.filter(user=self.request.user).count()
        context['total_guests'] = EventRegistration.objects.filter(
            event__user=self.request.user).count()
        return context
    

class CreateEventView(LoginRequiredMixin, TemplateView):
    template_name = 'organizer/newEvent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateEventForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()

            event_datetime = datetime.combine(event.date, event.time)
            reminder = event_datetime - datetime.timedelta(hours=24)
            if reminder > timezone.now():
                follow_email_to_guests.apply_async(
                    args=[event.id], eta=reminder
                )

            return redirect('org-dashboard')
        
        return self.render_to_response({'form': form})


class MyEventsView(LoginRequiredMixin, EventFilterMixin, TemplateView):
    template_name = 'organizer/my_events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.filter(user=self.request.user).annotate(
            guests=Count('registrations'))
        events = self.filter_queryset(events)
        context['events'] = events
        context['categories'] = Event.Category.choices
        return context
    

class EditEventView(TemplateView):
    template_name = 'organizer/editEvent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        context['event'] = event
        context['form'] = EditEventForm(instance=event)
        return context
    
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        form = EditEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('view_event', pk=event.pk)
        return self.render_to_response({'form': form, 'event': event})
    

class DeleteEventView(LoginRequiredMixin, View):
    model = Event
    success_url = reverse_lazy('my_events')

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        event.delete()
        return redirect('my_events')
    

class GuestsListView(TemplateView):
    template_name = 'organizer/guests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'], user=self.request.user)
        guests = EventRegistration.objects.filter(event=event).select_related('user')
        context['guests'] = guests
        context['event'] = event
        context['total_guests'] = guests.count()
        return context

class ExportGuestsCSVView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Dispostion'] = 'attachment; filename="guests_list.csv"'

        writer = csv.writer(response)
        writer.writerow(['Event Title', 'Attendee Name', 'Email', 'Phone', 'Registered On'])
        events = Event.objects.filter(user=request.user).prefetch_related('registrations__user')

        for event in events:
            for registration in event.registrations.all():
                user = registration.user
                writer.writerow([
                    event.title, user.name, user.email, user.phone, registration.created_at
                ])

        return response
    

class FollowUpMailView(View):
    def post(self, request, id):
        event = get_object_or_404(Event, id=id)

        if event.user != request.user:
            return redirect('view_event', pk=id)
        
        follow_email_to_guests(id)
        return redirect('org-dashboard')


class AnalyticsView(TemplateView):
    template_name = 'organizer/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events'] = Event.objects.filter(user=self.request.user).count()
        context['total_guests'] = EventRegistration.objects.filter(
            event__user=self.request.user).count()
        context['monthly_data'] = get_monthly_registration_data(self.request.user)
        context['top_events'] = get_top_events(self.request.user)
        context['recent_registrations'] = EventRegistration.objects.all().order_by('-created_at')[:5]
        return context
    

# ****************************** Admin Views ***********************************

class AdmindashboardView(TemplateView):
    template_name = "admin/admin_dashboard.html"
