from __future__ import absolute_import
from django.db import models
from accounts.models import Patient, Doctor, Hospital

##The model that creates the appointment.
class AppointmentManager(models.Manager):
    def create_appt(self, patient, doctor, date, hospital):
        appt = self.create(patient=patient, doctor=doctor, date=date, hospital=hospital)
        return appt
##Appointment Model, assigns the model fields to the appointment
class Appointment(models.Model):
    patient = models.ForeignKey(Patient)
    doctor = models.ForeignKey(Doctor)
    date = models.DateTimeField()
    hospital = models.ForeignKey(Hospital)
    objects = AppointmentManager()
    
