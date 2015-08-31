from django.contrib import admin
from .models import Prescription

# this is a display format for appointments in the admin console
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient',  'hospital')

#registers appointments and the appointment admin with the admin console
admin.site.register(Prescription, PrescriptionAdmin)
