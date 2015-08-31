from __future__ import absolute_import
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Patient
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from accounts.models import Hospital, Doctor, Nurse
from logger.models import Entry
import datetime

gender_choices =(
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other?"),
)

# the form for patient creation  
class PatientForm(UserCreationForm):
    # all the fields for the form
    email = forms.EmailField(required = False)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    address = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)
    insurance = forms.CharField(max_length=10, required = False)
    ice_name = forms.CharField(max_length=50, required=False)
    ice_phone = forms.CharField(max_length=15, required=False)
    med_info = forms.CharField(max_length=500, required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="None")
    pref_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Preferred Hospital]")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Doctor]")
    nurse = forms.ModelMultipleChoiceField(queryset=Nurse.objects.all(), required = False, widget=forms.SelectMultiple(attrs={'class':'selectpicker show-tick form-control'}))
    sex = forms.ChoiceField(choices=gender_choices, required = False, widget=forms.Select(attrs={'class':'selectpicker form-control'}))
    weight = forms.IntegerField(required=False)
    height_ft = forms.IntegerField(required=False)
    height_in = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    # called by form.save(), this commits the information entered into a new patient
    def save(self,commit = True):   
        user = super(PatientForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        if commit:
            user.save()
            g, created = Group.objects.get_or_create(name="Patient")
            g.user_set.add(user)
            patient = Patient.objects.create(user=user)
            patient.address = self.cleaned_data['address']
            patient.phone_number = self.cleaned_data['phone']
            patient.insurance_id = self.cleaned_data['insurance']
            patient.ice_name = self.cleaned_data['ice_name']
            patient.ice_phone = self.cleaned_data['ice_phone']
            patient.hospital = self.cleaned_data['hospital']
            patient.pref_hospital = self.cleaned_data['pref_hospital']
            patient.med_info = self.cleaned_data['med_info']
            patient.doctor = self.cleaned_data['doctor']
            patient.nurse = self.cleaned_data['nurse']
            patient.weight = self.cleaned_data['weight']
            patient.height_in = self.cleaned_data['height_in']
            patient.height_ft = self.cleaned_data['height_ft']
            patient.sex = self.cleaned_data['sex']
            patient.save()
            Entry.objects.create_entry(user, 'user_created', datetime.datetime.now())
        return user

    # checks if the user enters both a name and number for their emergency contact
    def clean(self):
        cleaned_data = super(PatientForm, self).clean()
        ice_name = cleaned_data.get("ice_name")
        ice_phone = cleaned_data.get("ice_phone")

        if any( [ice_name is not "" and ice_phone is "", ice_phone is not "" and ice_name is ""] ):
                raise forms.ValidationError("Both fields for Emergency Contact must be filled in")

        # Always return the full collection of cleaned data.
        return cleaned_data

# the form for doctor creation
class DoctorForm(UserCreationForm):
    # the fields for the form
    email = forms.EmailField(required = False)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    phone = forms.CharField(max_length=15, required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Hospital]")
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # called by form.save(), this commits the information entered into a new doctor    
    def save(self,commit = True):
        user = super(DoctorForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        user.is_staff = True
        if commit:
            user.save()
            g, created = Group.objects.get_or_create(name="Doctor")
            g.user_set.add(user)
            doctor = Doctor.objects.create(user=user)
            doctor.phone_number = self.cleaned_data['phone']
            doctor.hospital = self.cleaned_data['hospital']
            doctor.save()
            Entry.objects.create_entry(self.instance, 'doctor_user_created', datetime.datetime.now())
        return user

    
# the form for nurse creation
class NurseForm(UserCreationForm):
    # the fields for the form
    email = forms.EmailField(required = False)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    phone = forms.CharField(max_length=15, required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = True, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Hospital]")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # called by form.save(), this commits the information entered into a new nurse    
    def save(self,commit = True):   
        user = super(NurseForm, self).save()
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        user.is_staff = True
        if commit:
            user.save()
            g, created = Group.objects.get_or_create(name="Nurse")
            g.user_set.add(user)
            nurse = Nurse.objects.create(user=user)
            nurse.phone_number = self.cleaned_data['phone']
            nurse.hospital = self.cleaned_data['hospital']
            nurse.save()
            Entry.objects.create_entry(self.instance, 'nurse_user_created', datetime.datetime.now())
        return user

# the form for admin creation    
class AdminForm(UserCreationForm):
    # all of the fields form the form
    email = forms.EmailField(required = False)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    # called by form.save(), this commits the information entered into a new admin  
    def save(self,commit = True):   
        user = super(AdminForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
            Entry.objects.create_entry(self.instance, 'admin_user_created', datetime.datetime.now())
        return user 

# the form for updating user information       
class UpdateUserForm(UserChangeForm):
    # all of the fields form the form, not all of them are always used
    email = forms.EmailField(required = False)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    address = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=15, required=False)
    insurance = forms.CharField(max_length=10, required = False)
    ice_name = forms.CharField(max_length=50, required=False)
    ice_phone = forms.CharField(max_length=15, required=False)
    med_info = forms.CharField(max_length=500, required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Hospital]")
    pref_hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Prefered Hospital]")
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required = False, widget=forms.Select(attrs={'class':'selectpicker show-tick form-control'}), empty_label="[Doctor]")
    nurse = forms.ModelMultipleChoiceField(queryset=Nurse.objects.all(), required = False, widget=forms.SelectMultiple(attrs={'class':'selectpicker show-tick form-control'}))
    sex = forms.ChoiceField(choices=gender_choices, required = False, widget=forms.Select(attrs={'class':'selectpicker form-control'}))
    weight = forms.IntegerField(required=False)
    height_ft = forms.IntegerField(required=False)
    height_in = forms.IntegerField(required=False)
    docfile = forms.FileField(label='Upload Patient Information', required = False)

    # initializes form values
    def __init__(self, *args, **kwargs):
        self.editor = kwargs.pop('editor', None)
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        if(Group.objects.get(name="Patient") in self.instance.groups.all()):
            self.fields['hospital'].empty_label = "None"
            if self.instance is not None and get_user_object(self.instance).pref_hospital is not None:
                self.initial['pref_hospital'] = get_user_object(self.instance).pref_hospital.id
            if self.instance is not None and get_user_object(self.instance).hospital is not None:
                self.initial['hospital'] = get_user_object(self.instance).hospital.id
            if self.instance is not None and get_user_object(self.instance).doctor is not None:
                self.initial['doctor'] =  get_user_object(self.instance).doctor.id
            self.initial['nurse'] = [c.pk for c in get_user_object(self.instance).nurse.all()]
            self.initial['sex'] = get_user_object(self.instance).sex
        if(Group.objects.get(name="Nurse") in self.instance.groups.all() or Group.objects.get(name="Doctor") in self.instance.groups.all()):
            nurse = get_user_object(self.instance)
            if nurse.hospital is not None:
                self.initial['hospital'] = nurse.hospital.id
    class Meta:
        model = User
        fields = ('username', 'email', 'ice_name', 'ice_phone')

    # checks for errors in the form
    def clean(self):
        cleaned_data = super(UpdateUserForm, self).clean()
        
        # checks if the user enters both a name and number for their emergency contact
        if get_user_type(self.instance) is "Patient":
            file = self.cleaned_data.get("docfile")
            if(file is not None):
                file_type = file.name.split('.')[1]

                if len(file.name.split('.')) == 1:
                    raise forms.ValidationError('File type is not supported')

                if file_type != 'csv':
                    raise forms.ValidationError('File type is not supported')

            ice_name = cleaned_data.get("ice_name")
            ice_phone = cleaned_data.get("ice_phone")
            if ice_name != "" and ice_phone is "":
                raise forms.ValidationError("Both fields for Emergency Contact must be filled in")
            elif ice_phone != "" and ice_name is "":
                 raise forms.ValidationError("Both fields for Emergency Contact must be filled in")
                
        if Group.objects.get(name="Nurse") in self.instance.groups.all() and cleaned_data.get("hospital") is None:
            raise forms.ValidationError({'hospital': ["This field is required"]})
        # Always return the full collection of cleaned data.
        return cleaned_data
    
    def clean_password(self):
        return self.cleaned_data['password']

    # called by form.save(), this commits the information entered into the user 
    def save(self,commit = True):   
        user = super(UpdateUserForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        if(get_user_type(user) != "Patient"):
            user.is_staff = True
            if(get_user_type(user) == "Admin"):
                user.is_superuser = True
                
        if commit:
            user.save()
            # different user types do different things to save their data
            if(Group.objects.get(name="Patient") in user.groups.all()):
                patient = get_user_object(user)
                patient.address = self.cleaned_data['address']
                patient.phone_number = self.cleaned_data['phone']
                patient.insurance_id = self.cleaned_data['insurance']
                patient.ice_name = self.cleaned_data['ice_name']
                patient.ice_phone = self.cleaned_data['ice_phone']
                if(get_user_type(self.editor) == "Admin"):
                    patient.hospital = self.cleaned_data['hospital']
                patient.pref_hospital = self.cleaned_data['pref_hospital']
                patient.med_info = self.cleaned_data['med_info']
                if(patient.doctor != self.cleaned_data['doctor']):
                    Entry.objects.create_entry(user, 'patient_changed_doctors', datetime.datetime.now())
                if(get_user_type(self.editor) == "Admin" or get_user_type(self.editor) == "Patient"):
                    patient.doctor = self.cleaned_data['doctor']
                if(get_user_type(self.editor) != "Patient"):
                    patient.nurse = self.cleaned_data['nurse']
                patient.weight = self.cleaned_data['weight']
                patient.height_in = self.cleaned_data['height_in']
                patient.height_ft = self.cleaned_data['height_ft']
                patient.sex = self.cleaned_data['sex']
                patient.save()
            elif(Group.objects.get(name="Doctor") in user.groups.all()):
                usr =  get_user_object(user)
                usr.phone_number = self.cleaned_data['phone']
                usr.hospital = self.cleaned_data['hospital']
                usr.save()
            elif(Group.objects.get(name="Nurse") in user.groups.all()):
                usr = get_user_object(user)
                usr.phone_number = self.cleaned_data['phone']
                usr.hospital = self.cleaned_data['hospital']
                usr.save()
        return user

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
