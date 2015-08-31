from __future__ import absolute_import
from django.db import models
from django.contrib.auth.models import User
import datetime

class MessageManager(models.Manager):
    def create_message(self, sender, recipient, text, subject):
        message = self.create(sender = sender, recipient = recipient, text = text, subject = subject, date = datetime.datetime.now())
        return message

class Message(models.Model):
    sender = models.ForeignKey(User)
    recipient = models.ForeignKey(User, related_name='recipient')
    text = models.CharField(max_length=1000)
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    viewed = models.BooleanField(default=False)
    objects = MessageManager()
    class Meta:
        verbose_name = 'Message'
    def __str__(self):
        return self.subject
        
    def cutToSize(self):
        if len(self.text) > 40:
            return self.text[:40] + "..."
        else:
            return self.text

