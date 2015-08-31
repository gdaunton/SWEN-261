from __future__ import absolute_import
from django import forms
from .models import Test
from logger.models import Entry
import datetime

class NewTestForm(forms.Form):
        name = forms.CharField(max_length=100, required = True)
        notes = forms.CharField(max_length= 500, required = False)
        docfile = forms.FileField(label='Add files', required = False)
		
        def __init__(self, *args, **kwargs):
                self.doctor = kwargs.pop('doctor', None)
                self.patient = kwargs.pop('patient', None) 
                super(NewTestForm, self).__init__(*args, **kwargs) 

        def save(self):
                name = self.cleaned_data['name']
                notes = self.cleaned_data['notes']
                file = self.cleaned_data['docfile']
                test = Test.objects.create_test(name, notes, file, self.patient, self.doctor, datetime.datetime.now())
                return test

		
class EditTestForm(forms.Form):
        name = forms.CharField(max_length=100, required = True)
        notes = forms.CharField(max_length= 500, required = False)
        docfile = forms.FileField(label='Add files', required = False)
		
        def __init__(self, *args, **kwargs):
                self.test = kwargs.pop('test', None)
                self.doctor = kwargs.pop('doctor', None)
                self.patient = kwargs.pop('patient', None)
                super(EditTestForm, self).__init__(*args, **kwargs)
                self.initial['docfile'] = self.test.files

        def save(self):
                self.test.name = self.cleaned_data['name']
                self.test.notes = self.cleaned_data['notes']
                if(self.cleaned_data['docfile'] == False):
                        self.test.files = None
                self.test.save()
                return self.test
