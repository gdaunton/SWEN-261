from __future__ import absolute_import
from django.db import models
from accounts.models import Patient, Doctor, Hospital

##The model that creates the prescription.
class PrescriptionManager(models.Manager):
    def create_prescription(self, name, notes, patient, doctor, date, hospital):
        rx = self.create(name = name, notes = notes, patient=patient, doctor=doctor, date=date, hospital=hospital)
        return rx

##Prescription Model, assigns the model fields to the prescription
class Prescription(models.Model):
    name = models.CharField(max_length=100, blank=True)
    notes = models.CharField(max_length=500, blank=True)
    patient = models.ForeignKey(Patient, related_name='Patient')
    doctor = models.ForeignKey(Doctor, related_name='Doctor')
    date = models.DateField()
    hospital = models.ForeignKey(Hospital)
    objects = PrescriptionManager()
    class Meta:
        verbose_name = 'Prescription'
    def __str__(self):
        return self.name
