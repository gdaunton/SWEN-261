from django.contrib import admin
from .models import Entry

#EntryAdmin sets a format for displaying entries on the admin console
class EntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'action')
    list_filter = ['user']

#this registers the Entry class and the EntryAdmin class with the admin console
admin.site.register(Entry, EntryAdmin)
