from __future__ import absolute_import
from django.db import models
from accounts.models import Patient, Doctor, Hospital

from django import forms
from logger.models import Entry
import datetime
import os
##The model that creates the test
class TestManager(models.Manager):
    def create_test(self, name, notes, files, patient, doctor, date):
        tst = self.create(name = name, notes = notes, files=files, patient=patient, doctor=doctor, date=date)
        return tst

IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]

##Test Model, assigns the model fields to the test
class Test(models.Model):
    name = models.CharField(max_length=100, blank=True)
    notes = models.CharField(max_length=500, blank=True)
    patient = models.ForeignKey(Patient, related_name='Test_Patient', null=True)
    files = models.FileField(upload_to= 'tests', null=True) 
    doctor = models.ForeignKey(Doctor, related_name='Test_Doctor', null=True)
    date = models.DateField()
    released = models.BooleanField(default=False)
    objects = TestManager()
    class Meta:
        verbose_name = 'Test'
    def __str__(self):
        return self.name
    def filename(self):
        return os.path.basename(self.files.name)
    def has_image(self):
        return any([self.files.url.endswith(e) for e in IMAGE_EXTENSIONS]) 
