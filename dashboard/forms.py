from __future__ import absolute_import
from django import forms
from accounts.models import Hospital, Hours
from django.contrib.auth.models import User

class HospitalForm(forms.Form):
    name = forms.CharField(required = True)
    location = forms.CharField(required = True)
    week_open = forms.CharField(required = False)
    week_close = forms.CharField(required = False)
    sat_open = forms.CharField(required = False)
    sat_close = forms.CharField(required = False)
    sun_open = forms.CharField(required = False)
    sun_close = forms.CharField(required = False)

    class Meta:
        model = Hospital

    def clean(self):
        cleaned_data = super(HospitalForm, self).clean()
        name = cleaned_data.get("name")
        if Hospital.objects.filter(name=name).count() != 0:
            raise forms.ValidationError("That name is already taken")
        return cleaned_data
	
    ## Save the hospital to the database
    def save(self):
        name = self.cleaned_data['name']
        location = self.cleaned_data['location']
        weekdays_open = self.cleaned_data['week_open']
        weekdays_close = self.cleaned_data['week_close']
        sat_open = self.cleaned_data['sat_open']
        sat_close = self.cleaned_data['sat_close']
        sun_open = self.cleaned_data['sun_open']
        sun_close = self.cleaned_data['sun_close']
        hos = Hospital.objects.create_hospital(name, location)
        if(weekdays_open is not None and weekdays_close is not None):
            Hours.objects.create_hours(hos, "Weekdays", weekdays_open, weekdays_close)
        if(sat_open is not None and sat_close is not None):
            Hours.objects.create_hours(hos, "Sat", sat_open, sat_close)
        if(sun_open is not None and sun_close is not None):
            Hours.objects.create_hours(hos, "Sun", sun_open, sun_close)
        return hos

gender_choices =(
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other?"),
)

class MedInfoForm(forms.Form):
    med_info = forms.CharField(max_length=500, required=False)
    sex = forms.ChoiceField(choices=gender_choices, required = False, widget=forms.Select(attrs={'class':'selectpicker form-control'}))
    weight = forms.IntegerField(required=False)
    height_ft = forms.IntegerField(required=False)
    height_in = forms.IntegerField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MedInfoForm, self).__init__(*args, **kwargs)
        self.initial['sex'] = self.user.sex

    class Meta:
        model = User
    
    ## Save the hospital to the database
    def save(self):
        self.user.med_info = self.cleaned_data['med_info']
        self.user.sex = self.cleaned_data['sex']
        self.user.weight = self.cleaned_data['weight']
        self.user.height_ft = self.cleaned_data['height_ft']
        self.user.height_in = self.cleaned_data['height_in']
        self.user.save()
        return self.user
