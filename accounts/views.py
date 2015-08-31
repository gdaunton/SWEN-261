from __future__ import absolute_import
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from accounts.forms import PatientForm, NurseForm, DoctorForm, AdminForm
from django.template import RequestContext
from django.contrib.auth.models import Group
from django.contrib.auth.views import login
import csv
from tests.models import Test
from accounts.models import Patient, Doctor, Nurse
from django.contrib.auth.models import User

# redirrects already logged in users to home
def custom_login(request, template_name):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/home/')
    else:
        return login(request, template_name)

# view for registering a new user
def register_user(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = PatientForm()
    return render_to_response('accounts/register.html', {'type': get_user_type(request.user), 'u_type':'Patient', 'form':form}, context_instance = RequestContext(request))

# view for registering a new admin
def register_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = AdminForm()
    return render_to_response('dashboard/add_user.html', {'type': get_user_type(request.user), 'u_type':'Admin', 'form':form}, context_instance = RequestContext(request))

# view for registering a new patient
def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = PatientForm()
    return render_to_response('dashboard/add_user.html', {'type': get_user_type(request.user), 'u_type':'Patient', 'form':form}, context_instance = RequestContext(request))

# view for registering a new doctor
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = DoctorForm()
    return render_to_response('dashboard/add_user.html', {'type': get_user_type(request.user), 'u_type':'Doctor', 'form':form}, context_instance = RequestContext(request))

# view for registering a new nurse
def register_nurse(request):
    if request.method == 'POST':
        form = NurseForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/home/')
    else:
        form = NurseForm()
    return render_to_response('dashboard/add_user.html', {'type': get_user_type(request.user), 'u_type':'Nurse', 'form':form}, context_instance = RequestContext(request))

def export_info(request, name):
    user = User.objects.filter(username = name)[0]
    patient = get_user_object(user)
    test_results = Test.objects.filter(patient = patient, released=True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patientinfo.csv"'
    writer = csv.writer(response)
    writer.writerow(['PN', user.first_name, user.last_name])
    writer.writerow(['PE', user.email, patient.address, patient.phone_number, patient.insurance_id])
    if(patient.nurse.count() != 0):
        writer.writerow(['PD', patient.doctor, patient.nurse.all()[0], patient.hospital])
    else:
        writer.writerow(['PD', patient.doctor, "", patient.pref_hospital])    
    writer.writerow(['PICE', patient.ice_name, patient.ice_phone])
    writer.writerow(['PTR', test_results.count()])
    for test in test_results:
        writer.writerow(['TR', test.name, test.patient, test.doctor, test.notes, test.date])

    return response

# get the type of the user that is given
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
        u_type = None
    return u_type
