from __future__ import absolute_import
from django import forms
from accounts.models import Hospital, Doctor, Patient, Nurse
from logger.models import Entry
from .models import Appointment
from django.utils import timezone
import datetime
from django.contrib.auth.models import Group, User


##Form to represent a single appointment.
##Has fields for patient, doctor and hospital.
class AppointmentForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Patient]")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Doctor]")
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Hospital]")
    date = forms.CharField(max_length= 100, required = True)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        user_profile = get_user_object(self.user)
        patient = kwargs.pop('patient', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)
        if(patient != None):
            self.initial['patient'] = get_user_object(User.objects.filter(username=patient)[0])
        if get_user_type(self.user) is "Patient":
            if self.user is not None and user_profile.hospital is not None:
                self.initial['hospital'] = user_profile.hospital.id
            if self.user is not None and user_profile.doctor is not None:
                self.initial['doctor'] = user_profile.doctor.id
    class Meta:
        model = Appointment
            
    def clean(self):        ## Cleans data and checks appointment for specified conflicts
        cleaned_data = super(AppointmentForm, self).clean()
        user_profile = get_user_object(self.user)
        if(self.cleaned_data.get('hospital') is not None):
            hospital = self.cleaned_data.get('hospital')
            if get_user_type(self.user) is "Doctor":
                doctor = user_profile
            else:
                doctor = self.cleaned_data.get('doctor')
            if get_user_type(self.user) is "Patient":
                patient = user_profile
            else:
                patient = self.cleaned_data.get('patient')
            locations = Hospital.objects.filter(doctor=doctor, pk=hospital.id)
            ##invalid location
            if(locations.count() == 0):
                raise forms.ValidationError("That Doctor is not available at that location")
            ##time conflict
            if(doctor is not None and patient is not None and self.cleaned_data.get('date') is not None):
                act_date = timezone.make_aware(datetime.datetime.strptime(self.cleaned_data.get('date'), "%m/%d/%Y %I:%M %p"), timezone.get_default_timezone())
                for appt in Appointment.objects.filter(doctor=doctor):
                    if(appt.date == act_date):
                        raise forms.ValidationError("There is already an appointment at this time for that doctor")
                for appt in Appointment.objects.filter(patient=patient):
                    if(appt.date == act_date):
                        raise forms.ValidationError("There is already an appointment at this time for that patient")
            else:    
                if get_user_type(self.user) is "Doctor":
                    raise forms.ValidationError({'patient': ["This field is required"]})
                if get_user_type(self.user) is "Patient":
                    raise forms.ValidationError({'doctor': ["This field is required"]})
        return cleaned_data

    ## Save the appointment to the database
    def save(self): 
        hospital = self.cleaned_data['hospital']
        date = self.cleaned_data['date']
        if get_user_type(self.user) is "Doctor":
                doctor = get_user_object(self.user)
        else:
            doctor = self.cleaned_data['doctor']
        if get_user_type(self.user) is "Patient":
            patient = get_user_object(self.user)
        else:
            patient = self.cleaned_data['patient']
        act_date = timezone.make_aware(datetime.datetime.strptime(date, "%m/%d/%Y %I:%M %p"), timezone.get_default_timezone())
        Entry.objects.create_entry(self.user, 'appointment_created', datetime.datetime.now())
        appt = Appointment.objects.create_appt(patient, doctor, act_date, hospital)
        return appt

##Class to represent the form for editing appointments
##Can be used to edit any existing appointment
class AppointmentEditForm(forms.Form):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Patient]")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Doctor]")
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control', 'required': ''}), empty_label="[Hospital]")
    date = forms.CharField(max_length= 100, required = True)
    def __init__(self, *args, **kwargs):
        appt = kwargs.pop('appt', None)
        self.user = kwargs.pop('user', None)
        super(AppointmentEditForm, self).__init__(*args, **kwargs)
        
        if self.user is not None and appt is not None:
            self.initial['hospital'] = appt.hospital.id
        if self.user is not None and appt is not None:
            self.initial['doctor'] = appt.doctor.id
        if self.user is not None and appt is not None:
            self.initial['patient'] = appt.patient.id
            
        if get_user_type(self.user) is "Patient":
            self.initial['patient'] = get_user_object(self.user)
        elif get_user_type(self.user) is "Doctor":
            self.initial['doctor'] = get_user_object(self.user)
    class Meta:
        model = Appointment
            
    def clean(self, *args, **kwargs):
        curr_appt = kwargs.pop('appt', None)
        cleaned_data = super(AppointmentEditForm, self).clean()
        
        if(self.cleaned_data.get('hospital') is not None):
            hospital = self.cleaned_data.get('hospital')
            if get_user_type(self.user) is "Doctor":
                doctor = get_user_object(self.user)
            else:
                doctor = self.cleaned_data.get('doctor')
            if get_user_type(self.user) is "Patient":
                patient = get_user_object(self.user)
            else:
                patient = self.cleaned_data.get('patient')
            locations = Hospital.objects.filter(doctor=doctor, pk=hospital.id)
            if(locations.count() == 0):
                raise forms.ValidationError("That Doctor is not available at that location")
            if(doctor is not None and patient is not None and self.cleaned_data.get('date') is not None):
                act_date = timezone.make_aware(datetime.datetime.strptime(self.cleaned_data.get('date'), "%m/%d/%Y %I:%M %p"), timezone.get_default_timezone())
                for appt in Appointment.objects.filter(doctor=doctor):
                    if(appt.date == act_date and appt is not curr_appt):
                        raise forms.ValidationError("There is already an appointment at this time for that doctor")
                for appt in Appointment.objects.filter(patient=patient):
                    if(appt.date == act_date and appt is not curr_appt):
                        raise forms.ValidationError("There is already an appointment at this time for that patient")
            else:
                if get_user_type(self.user) is "Doctor":
                    raise forms.ValidationError({'patient': ["This field is required"]})
                if get_user_type(self.user) is "Patient":
                    raise forms.ValidationError({'doctor': ["This field is required"]})
        return cleaned_data
    #Update the appointment information and save to the database
    def save(self, *args, **kwargs):
        appt = kwargs.pop('appt', None)
        hospital = self.cleaned_data['hospital']
        date = self.cleaned_data['date']
        if get_user_type(self.user) is "Doctor":
                doctor = get_user_object(self.user)
        else:
            doctor = self.cleaned_data['doctor']
        if get_user_type(self.user) is "Patient":
            patient = get_user_object(self.user)
        else:
            patient = self.cleaned_data['patient']
        act_date = timezone.make_aware(datetime.datetime.strptime(date, "%m/%d/%Y %I:%M %p"), timezone.get_default_timezone())
        Entry.objects.create_entry(self.user, 'appointment_edited', datetime.datetime.now())
        appt.patient = patient
        appt.doctor = doctor
        appt.date = act_date
        appt.hospital = hospital
        appt.save()
        return appt

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
