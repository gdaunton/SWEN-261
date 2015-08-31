from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
  

class HospitalManager(models.Manager):
    def create_hospital(self, name, location):
        hospital = self.create(name=name, location=location)
        return hospital
		
#the model for a hospital that contains the name and location of the hospital
class Hospital(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=500)
    objects = HospitalManager()
    def __str__(self):
        return self.name
    
class HoursManager(models.Manager):
    def create_hours(self, hospital, day, start, close):
        hours = self.create(hospital=hospital, day=day, start=start, close=close)
        return hours
    
class Hours(models.Model):
    hospital = models.ForeignKey(Hospital)
    day = models.CharField(max_length=50)
    start = models.CharField(max_length = 100, blank=True)
    close = models.CharField(max_length = 100, blank=True)
    objects = HoursManager()
    def __str__(self):
        return self.day

#the model for the nurse, each nurse corresponds to one user
#and can also have a phone number and hospital
class Nurse(models.Model):
    user = models.OneToOneField(User)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    hospital = models.ForeignKey(Hospital, default=None, blank=True, null=True)
    class Meta:
        verbose_name = 'Nurse'
    def __str__(self):
        return self.user.username

#the model for the doctor, each doctor corresponds to one user
#and can also have a phone number and multiple hospitals
class Doctor(models.Model):
    user = models.OneToOneField(User)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    hospital = models.ForeignKey(Hospital, default=None, blank=True, null=True)
    class Meta:
        verbose_name = 'Doctor'
    def __str__(self):
        return self.user.username

#the model for the patient, each patient corresponds to one user
#and can also include an address, a phone number, an insurance ID
#have an assigned doctor and many assigned nurses
#one hospital, an emergency contact, and medical information
class Patient(models.Model):
    user = models.OneToOneField(User)
    address = models.CharField(max_length=100, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    insurance_id = models.CharField(max_length=10, blank=True)
    doctor = models.ForeignKey(Doctor, default=None, blank=True, null=True)
    nurse = models.ManyToManyField(Nurse, default=None, blank=True, null=True)
    hospital = models.ForeignKey(Hospital, default=None, blank=True, null=True, related_name = "admitted")
    pref_hospital = models.ForeignKey(Hospital, default=None, blank=True, null=True, related_name = "preferred")
    ice_name =  models.CharField(max_length=50, blank=True)
    ice_phone = models.CharField(max_length=15, validators=[phone_regex], blank=True)
    sex = models.CharField(max_length=6, blank=True)
    weight = models.CharField(max_length=10, blank=True, null=True)
    height_ft = models.CharField(max_length=10, blank=True, null=True)
    height_in = models.CharField(max_length=10, blank=True, null=True)
    med_info = models.CharField(max_length=500, blank=True)
    
    class Meta:
        verbose_name = 'Patient'
    def __str__(self):
        return self.user.username

#facilitates creation of new patient
def create_patient(sender, instance, created, **kwargs):
    if created:
        Patient.objects.create(user=instance)
 
#model for prescription, with a name patient and doctor
#it creates the permissions for who can view/add/remove presceriptions
#this will be fully implemented in R2
class Prescription(models.Model):
    name = models.CharField(max_length=100)
    patient = models.ForeignKey(Patient)
    doctor = models.ForeignKey(Doctor)
    class Meta:
        permissions = (
            ("view_pers", "Can view prescription"),
            ("add_pers", "Can add prescription"),
            ("remove_pers", "Can remove prescription"),
        )
