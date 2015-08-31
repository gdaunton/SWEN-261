from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Prescription
from .forms import PrescriptionForm
import datetime
from django.utils import timezone
from django.contrib.auth.models import Group
from accounts.models import Nurse, Patient, Doctor
from logger.models import Entry


# checks if user is a doctor, used for user_passes_test
def doctor_check(user):
    return get_user_type(user) is 'Doctor'

##Main view for the prescription list
@login_required(login_url='/login/')
def main(request):
    #Checks user type
    if(Group.objects.get(name="Patient") in request.user.groups.all()):
        rx_list = Prescription.objects.filter(patient=get_user_object(request.user))
    elif(Group.objects.get(name="Doctor") in request.user.groups.all()):
        rx_list = Prescription.objects.filter(doctor=get_user_object(request.user))
    elif(Group.objects.get(name="Nurse") in request.user.groups.all()):
        rx_list = Prescription.objects.filter(hospital=get_user_object(request.user).hospital)
    else:
        rx_list = Prescription.objects.all()
    return render_to_response('prescriptions/scripts.html', {'prescriptions':rx_list, 'type':get_user_type(request.user)}, context_instance=RequestContext(request))

##View for the add prescription page
@login_required(login_url='/login/')
@user_passes_test(doctor_check)
def add(request, template_name = 'prescriptions/add.html'):
    type = get_user_type(request.user)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/scripts/')
    else:
        form = PrescriptionForm(user=request.user)
    return render_to_response(template_name, {'form':form, 'type':get_user_type(request.user)}, context_instance = RequestContext(request))

##View for deleting a prescription.
@login_required(login_url='/login/')
@user_passes_test(doctor_check)
def delete(request, pk):
    rx = Prescription.objects.filter(pk=pk)[0].delete()
    Entry.objects.create_entry(request.user, 'prescription_removed', datetime.datetime.now())
    return HttpResponseRedirect('/scripts/')       #Redirects to prescription list

one_day = datetime.timedelta(days=1)

##Helper function to get the week of the date specified
##Used to assist sorting and displaying appointments
def get_week(date):
    day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
    sunday = date - datetime.timedelta(days=day_idx)
    date = sunday
    days = []
    for n in [1,2,3,4,5,6,7]:
        days.append(date)
        date += one_day
    return days
##Returns the type of the user specified
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
