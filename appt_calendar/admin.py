from django.contrib import admin
from .models import Appointment

# this is a display format for appointments in the admin console
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'hospital')
    list_filter = ['date']

#registers appointments and the appointment admin with the admin console
admin.site.register(Appointment, AppointmentAdmin)
