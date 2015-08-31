from django.contrib import admin
from .models import Message

#sets a format for the django admin console display for messages
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject' )
    list_filter = ['sender']

#registers message and message admin with the admin console
admin.site.register(Message, MessageAdmin)
