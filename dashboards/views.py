from django.shortcuts import render
from django.views.generic import TemplateView

from dashboards.forms import CreateEventForm

# Create your views here.
class CreateEventView(TemplateView):
    template_name = 'newEvent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateEventForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)