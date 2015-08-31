from __future__ import absolute_import
from django import forms
from accounts.models import Hospital, Doctor, Patient, Nurse
from logger.models import Entry
from .models import Prescription
from django.utils import timezone
import datetime
from django.contrib.auth.models import Group
from logger.models import Entry


##Form to represent a single prescription.
##Has fields for name, notes, patient, doctor, date, and hospital
class PrescriptionForm(forms.Form):
    name = forms.CharField(max_length= 25, required = True)
    notes = forms.CharField(max_length= 500, required = False)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Patient]")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Doctor]")
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Hospital]")
    date = forms.CharField(max_length= 100, required = True)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        user_profile = get_user_object(self.user)
        super(PrescriptionForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Prescription
            
    def clean(self):        ## Cleans data
        cleaned_data = super(PrescriptionForm, self).clean()
        user_profile = get_user_object(self.user)
        if(self.cleaned_data.get('hospital') is not None):
            hospital = self.cleaned_data.get('hospital')
            if get_user_type(self.user) is "Doctor":
                doctor = user_profile
            patient = self.cleaned_data.get('patient')
        return cleaned_data

    ## Save the prescription to the database
    def save(self):
        name = self.cleaned_data['name']
        notes = self.cleaned_data['notes']
        hospital = self.cleaned_data['hospital']
        date = self.cleaned_data['date']
        doctor = get_user_object(self.user)
        patient = self.cleaned_data['patient']
        act_date = timezone.make_aware(datetime.datetime.strptime(date, "%m/%d/%Y"), timezone.get_default_timezone())
        rx = Prescription.objects.create_prescription( name, notes, patient, doctor, act_date, hospital)
        Entry.objects.create_entry(self.user, 'prescription_created', datetime.datetime.now())
        return rx

#Returns the type of user that is currently being examined
def get_user_type(user):
    u_type = ""
    
    if(Group.objects.get(name="Patient") in user.groups.all()):
        u_type = "Patient"
    elif(Group.objects.get(name="Doctor") in user.groups.all()):
        u_type = "Doctor"
    elif(Group.objects.get(name="Nurse") in user.groups.all()):
        u_type = "Nurse"
    elif(user.is_superuser):
        u_type = "Admin"
    else:
        u_type = "Unknown"
    return u_type

#Returns the object representation of the selected user
def get_user_object(user):
    if(Group.objects.get(name="Patient") in user.groups.all()):
        u_type = Patient.objects.filter(user=user)[0]
    elif(Group.objects.get(name="Doctor") in user.groups.all()):
        u_type = Doctor.objects.filter(user=user)[0]
    elif(Group.objects.get(name="Nurse") in user.groups.all()):
        u_type = Nurse.objects.filter(user=user)[0]
    else:
        u_type = user
    return u_type
