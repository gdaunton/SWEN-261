from __future__ import absolute_import
from django import forms
from django.contrib.auth.models import User
from .models import Message
from django.utils import timezone
import datetime

class MessageForm(forms.Form):
    receiver = forms.ModelChoiceField(queryset=User.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker form-control', 'required': '', 'data-live-search':'true'}), empty_label="[User]")
    subject = forms.CharField(required = True)
    message = forms.CharField(required = True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        receiver = kwargs.pop('recipient', None)
        super(MessageForm, self).__init__(*args, **kwargs)
        self.initial['receiver'] = receiver

    class Meta:
        model = Message

    ## Save the appointment to the database
    def save(self):
        sender = self.user
        receiver = self.cleaned_data['receiver']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        mess = Message.objects.create_message(sender, receiver, message, subject)
        return mess
