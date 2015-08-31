from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.template import RequestContext
from logger.models import Entry
from accounts.models import Doctor, Patient, Nurse
from .models import Test
from .forms import EditTestForm, NewTestForm
from django.contrib.auth.decorators import login_required
import datetime

def view(request, name, pk):
    test = Test.objects.filter(pk=pk)[0]
    if((get_user_type(request.user) is 'Admin') or ((get_user_object(request.user).id is test.patient.id and test.released) or (get_user_object(request.user).id is test.doctor.id))):
        return render_to_response('tests/tests.html', {'test':test, 'type':get_user_type(request.user)}, context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()

def release(request, pk):
	test = Test.objects.filter(pk=pk)[0]
	test.released = not test.released
	test.save()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
def add(request, name):
    user = User.objects.filter(username=name)[0]
    if(get_user_type(user) == "Patient" and get_user_object(request.user).id is get_user_object(user).doctor.id):
        if request.method == 'POST':
            form = NewTestForm(request.POST, request.FILES, doctor=get_user_object(request.user), patient=get_user_object(user))
            if form.is_valid():
                test = form.save()
                try:
                    if (request.FILES['docfile']):
                        test.files = request.FILES['docfile']
                        test.save()
                except:
                    t = True
                Entry.objects.create_entry(request.user, 'test_created_for_' + str(user), datetime.datetime.now())
                return HttpResponseRedirect('/user/' + str(user) + '/')
        else:
            form = NewTestForm(doctor=get_user_object(request.user), patient=get_user_object(user))
        return render_to_response('tests/add.html', {'form':form, 'doctor':get_user_object(request.user), 'patient':get_user_object(user), 'type':get_user_type(request.user)}, context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()

def edit(request, name, pk):
    user = User.objects.filter(username=name)[0]
    test = Test.objects.filter(pk=pk)[0]
    if(get_user_type(user) == "Patient" and get_user_object(request.user).id is get_user_object(user).doctor.id):
        if request.method == 'POST':
            form = EditTestForm(request.POST, request.FILES, doctor=get_user_object(request.user), patient=get_user_object(user), test=test)
            if form.is_valid():
                test = form.save()
                try:
                    if (request.FILES['docfile']):
                        test.files = request.FILES['docfile']
                        test.save()
                except:
                    t = True     
                Entry.objects.create_entry(request.user, 'test_edited_for_' + str(user), datetime.datetime.now())
                return HttpResponseRedirect('/user/' + str(user) + '/')
        else:
            form = EditTestForm(doctor=get_user_object(request.user), patient=get_user_object(user), test=test)
        return render_to_response('tests/add.html', {'form':form, 'test':test, 'doctor':get_user_object(request.user), 'patient':get_user_object(user), 'type':get_user_type(request.user)}, context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden()

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
