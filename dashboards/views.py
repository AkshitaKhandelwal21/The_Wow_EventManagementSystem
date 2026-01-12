from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboards.forms import CreateEventForm
from .models import Event, EventRegistration

# Create your views here.

class OrganizerDashboardView(TemplateView):
    template_name = 'organizer/organizer_dashboard.html'


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
        event_id = self.kwargs['id']
        context['event'] = get_object_or_404(
            Event.objects.select_related('user'), id=event_id
        )
        return context