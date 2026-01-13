from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboards.forms import CreateEventForm, EditEventForm
from .models import Event, EventRegistration

# Create your views here.

class OrganizerDashboardView(TemplateView):
    template_name = 'organizer/organizer_dashboard.html'

    
class UserDashboardView(TemplateView):
    template_name = "user/user_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registrations = EventRegistration.objects.filter(user=self.request.user).select_related(
            'event').order_by('created_at')[:3]
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
        context['events'] = Event.objects.filter(user=self.request.user)
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
        is_reg = EventRegistration.objects.filter(
            user=self.request.user, event=event).exists()
        attendees = EventRegistration.objects.filter(event=event).count()
        context['attendees'] = attendees
        context['is_reg'] = is_reg
        return context
    

class EditEventView(TemplateView):
    template_name = 'organizer/editEvent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        context['form'] = EditEventForm(instance=event)
        return context
    
    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        form = EditEventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('my_events')
        return self.render_to_response({'form': form})
    

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
        context['events'] = Event.objects.all()
        return context


class UserRegisterView(TemplateView):
    template_name = 'organizer/view_event.html'

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        register, created = EventRegistration.objects.get_or_create(
            user=request.user, event=event
        )
        if created:
            messages.success(request, "You have successfully registered for this event")
            if event.seats:
                event.seats -= 1
                event.save(update_fields=['seats'])
        else:
            messages.info(request, "You are already registered for this event")

        return redirect('view_event', pk=event.pk)   
    # Redirect to registered events page


class MyRegisteredEventsView(TemplateView):
    template_name = 'user/registered_events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tickets'] = EventRegistration.objects.filter(user=self.request.user)
        return context