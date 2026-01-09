from django import forms
from .models import Event, EventRegistration

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'venue', 'date', 'time', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What is the event?'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us more'
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Where is the event'
            })
        }