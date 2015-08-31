from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from django.contrib.auth.models import Group
from logger.models import Entry
from django.contrib.auth.models import User
import datetime
# Create your views here.

@login_required(login_url='/login/')
def main(request):
    received = Message.objects.filter(recipient=request.user).order_by('-date')
    sent = Message.objects.filter(sender=request.user).order_by('-date')
    return render_to_response('messaging/messages.html', {'type': get_user_type(request.user), 'received':received, 'sent':sent}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def compose(request, pk = None, user = None):
    recipient = None
    if(user != None):
        recipient = User.objects.filter(username=user)[0]
    subject = ""
    if(pk != None):
        mess = Message.objects.filter(pk=pk)[0]
        recipient = mess.sender
        subject = "RE: " + mess.subject
    if request.method == 'POST':
        data = request.POST.copy()
        form = MessageForm(data, user=request.user, recipient=recipient)
        if form.is_valid():
            form.save()
            Entry.objects.create_entry(request.user, 'user_sent_message', datetime.datetime.now())
            return HttpResponseRedirect('/messages/')
    else:
        form = MessageForm(user=request.user, recipient=recipient)
    return render_to_response('messaging/compose.html', {'subject':subject, 'user':request.user, 'form': form, 'type': get_user_type(request.user)}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def viewMessage(request, pk):
    message = Message.objects.get(pk=pk)
    message.viewed = True
    message.save()
    return render_to_response('messaging/message.html', {'type':get_user_type(request.user), 'message':message}, context_instance=RequestContext(request))
    

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
