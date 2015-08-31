from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Appointment
from .forms import AppointmentForm, AppointmentEditForm
import datetime
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from logger.models import Entry
from accounts.models import Doctor, Patient, Nurse

# checks if user is a patient or doctor, used for user_passes_test
def cancel_check(user):
    return get_user_type(user) is 'Patient' or get_user_type(user) is 'Doctor'

##Main view for the appointment calendar.
@login_required(login_url='/login/')
def main(request):
    appts = upcoming(request.user)
    return render_to_response('appt_calendar/calendar.html', {'appointments':appts, 'type':get_user_type(request.user)}, context_instance=RequestContext(request))

def upcoming(user):
    appts = []
    type = get_user_type(user)
    if(type == "Patient"):
        appts = Appointment.objects.filter(patient=get_user_object(user))
    elif(type == "Doctor"):
        appts = Appointment.objects.filter(doctor=get_user_object(user))
    elif(type == "Nurse"):
        for obj in Appointment.objects.filter(hospital=get_user_object(user).hospital):
            if(obj.date.date() in get_week(datetime.date.today())):
                appts.append(obj)
    elif(type == "Admin"):
        appts = Appointment.objects.all()
    return appts

# gets all of the date objects in the current week
one_day = datetime.timedelta(days=1)
def get_week(date):
    day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
    sunday = date - datetime.timedelta(days=day_idx)
    date = sunday
    days = []
    for n in [1, 2, 3, 4, 5, 6, 7]:
        days.append(date)
        date += one_day
    return days

##View for the add apointment page
@login_required(login_url='/login/')
def add(request, pat=None, template_name = 'appt_calendar/add.html'):
    u_type = get_user_type(request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user, patient=pat)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/appt/')
    else:
        form = AppointmentForm(user=request.user, patient=pat)
    return render_to_response(template_name, {'form':form, 'type':u_type, 'user': request.user}, context_instance = RequestContext(request))

##View for the edit appointment page
@login_required(login_url='/login/')
def edit(request, pk, template_name = 'appt_calendar/edit.html'):
    u_type = get_user_type(request.user)
    appt = Appointment.objects.filter(pk=pk)[0]
    if request.method == 'POST':
        form = AppointmentEditForm(request.POST, user=request.user, appt=appt)
        if form.is_valid():
            form.save(appt=appt)
            return HttpResponseRedirect('/appt/')
    else:
        form = AppointmentEditForm(user=request.user, appt=appt)
    date = timezone.localtime(appt.date, timezone.get_default_timezone())
    return render_to_response(template_name, {'form':form, 'appt': appt, 'type':u_type, 'date': date.strftime("%m/%d/%Y %I:%M %p")}, context_instance = RequestContext(request))

##View for deleting an appointment.
@login_required(login_url='/login/')
@user_passes_test(cancel_check)
def delete(request, pk):
    appt = Appointment.objects.filter(pk=pk)[0].delete()
    Entry.objects.create_entry(request.user, 'appointment_cancelled', datetime.datetime.now())
    return HttpResponseRedirect('/appt/')       #Redirects to appt page

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
        u_type = None
    return u_type
