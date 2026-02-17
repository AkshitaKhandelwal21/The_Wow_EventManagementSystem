from io import BytesIO
from django.http import HttpResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import qrcode
from dashboards.forms import CreateEventForm, EditEventForm
from .models import Event, EventRegistration
from django.utils.timezone import now
import csv
from django.db.models import Count

# Create your views here.

class OrganizerDashboardView(TemplateView):
    template_name = 'organizer/organizer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events'] = Event.objects.filter(user=self.request.user).count()
        context['total_attendees'] = EventRegistration.objects.filter(
            event__user=self.request.user).count()
        return context
    
class UserDashboardView(TemplateView):
    template_name = "user/user_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registrations = EventRegistration.objects.filter(user=self.request.user).select_related(
            'event').order_by('event__date')[:3]
        context['activities'] = registrations
        return context
    

class AdmindashboardView(TemplateView):
    template_name = "admin/admin_dashboard.html"


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
            return redirect('org-dashboard')
        return self.render_to_response({'form': form})


class MyEventsView(LoginRequiredMixin, TemplateView):
    template_name = 'organizer/my_events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(user=self.request.user).order_by('date', 'time')
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

        attendees = EventRegistration.objects.filter(event=event).count()
        context['attendees'] = attendees
        today = now().date()
        context['similar_events'] = Event.objects.filter(
            category = event.category, date__gte=today
        ).exclude(id=event.id)[:3]
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
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['event'] = get_object_or_404(Event, pk=self.kwargs['pk'])
    #     return context

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        event.delete()
        return redirect('my_events')
    

class AllEventsView(TemplateView):
    template_name = 'user/all_events.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.annotate(attendees_count=Count('registrations'))
        context['events'] = events
        # context['attendees_count'] = EventRegistration.objects.annotate(users=Count('user'))
        return context


class UserRegisterView(TemplateView):
    template_name = 'organizer/view_event.html'

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        register, created = EventRegistration.objects.get_or_create(
            user=request.user, event=event
        )
        if created:
            if event.seats:
                event.seats -= 1
                event.save(update_fields=['seats'])

        return redirect('view_event', pk=event.pk)   
    # Redirect to registered events page


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
    

class AttendeesListView(TemplateView):
    template_name = 'organizer/attendees.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.filter(user=self.request.user)
        attendees = EventRegistration.objects.filter(event__in=events)
        context['attendees'] = attendees
        context['total_attendees'] = attendees.count()
        return context


class ExportAttendeesCSVView(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Dispostion'] = 'attachment; filename="attendees_list.csv"'

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
