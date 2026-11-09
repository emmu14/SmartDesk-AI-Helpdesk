
from django import forms
from django.core.exceptions import ValidationError

from .models import Ticket, Comment


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = [
            'title',
            'description',
            'category',
            'department',
            'impact',
            'urgency',
            'attachment',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter ticket title'
            }),

            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your problem',
                'rows': 5
            }),
        }


class TicketStatusForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['status']

    def clean_status(self):
        new_status = self.cleaned_data['status']
        old_status = self.instance.status

        allowed_transitions = {
            'assigned': ['in_progress'],
            'in_progress': ['resolved'],
            'resolved': ['closed'],
            'closed': [],
        }

        if new_status == old_status:
            return new_status

        allowed = allowed_transitions.get(old_status, [])

        if new_status not in allowed:
            raise ValidationError(
                f"Cannot change status from {old_status} to {new_status}."
            )

        return new_status


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['message']

        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Write your message...',
                'rows': 4
            })
        }
