from __future__ import absolute_import
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.forms import UpdateUserForm
from .forms import HospitalForm
from accounts.models import Patient, Doctor, Nurse, Hospital, Hours
from messaging.models import Message
from dashboard.forms import MedInfoForm
from appt_calendar.models import Appointment
from logger.models import Entry
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from tests.models import Test
from prescriptions.models import Prescription
import datetime
import csv
from io import TextIOWrapper

# checks if user is an admin, used for user_passes_test
def admin_check(user):
    return user.is_superuser

# checks if user is an admin or doctor, used for user_passes_test
def edit_check(user):
    return user.is_superuser or get_user_type(user) is 'Doctor'

# checks if user is an admin, used for user_passes_test
def admit_check(user):
    return user.is_staff and not user.is_superuser

# the view for the home page, changes for each user
@login_required(login_url='/login/')
def home(request):
    patient = None
    if(Group.objects.filter(name="Patient").count() == 0):
        Group.objects.create(name="Patient")
    if(Group.objects.filter(name="Doctor").count() == 0):
        Group.objects.create(name="Doctor")
    if(Group.objects.filter(name="Nurse").count() == 0):
        Group.objects.create(name="Nurse")
    if(get_user_type(request.user) == "Doctor"):
        patient = Patient.objects.filter(doctor=get_user_object(request.user))	
    appts = upcoming(request.user)
    new_mess = Message.objects.filter(recipient=request.user, viewed=False).count()
    if(request.user.is_superuser):
        users = get_all_logged_in_users()
        return render_to_response('dashboard/admin_home.html', {'type':'Admin', 'users':users, 'new_mess':new_mess, 'log': Entry.objects.order_by('-date'), 'patients': Patient.objects.all(), 'doctors': Doctor.objects.all(), 'nurses': Nurse.objects.all(), 'appt':appts}, context_instance=RequestContext(request))
    else:
        return render_to_response('dashboard/home.html', {'type':get_user_type(request.user), 'new_mess':new_mess, 'appt':appts, 'patient_list':patient }, context_instance=RequestContext(request))
    
# puts out a list of all the logged in users
@user_passes_test(admin_check)
def user_list(request):
    users = get_all_logged_in_users()
    return render_to_response('dashboard/users.html', {'type':'Admin', 'users':users}, context_instance=RequestContext(request))

# puts out a list of all the hospitals
def hos_list(request):
    return render_to_response('dashboard/hos_list.html', {'type':get_user_type(request.user), 'hos':Hospital.objects.all()}, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def admit_patient(request, pk):
    patient = get_user_object(User.objects.filter(pk=pk)[0])
    if(patient.hospital == get_user_object(request.user).hospital):
        Entry.objects.create_entry(request.user, str(patient) + '_discharged_from_'+ str(patient.hospital), datetime.datetime.now())
        patient.hospital = None
    else:
        if(patient.hospital == None):
            Entry.objects.create_entry(request.user, str(patient) + '_admited_to_'+ str(get_user_object(request.user).hospital), datetime.datetime.now())
        else:
            Entry.objects.create_entry(request.user, str(patient) + '_transfered_to_'+ str(get_user_object(request.user).hospital), datetime.datetime.now())
        patient.hospital = get_user_object(request.user).hospital
    patient.save()
    
    return HttpResponseRedirect('/user/' + str(patient))       #Redirects to prescription list

# view for creating a new hospital
@user_passes_test(admin_check)
def add_hospital(request):
    if request.method == 'POST':
        form = HospitalForm(request.POST)     # create form object
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/hospitals/')
    else:
        form = HospitalForm()
    return render_to_response('dashboard/add_hos.html', {'type': get_user_type(request.user), 'u_type':'Nurse', 'form':form}, context_instance = RequestContext(request))


def hos_view(request, name):
    hos = Hospital.objects.get(name=name)
    doctors = Doctor.objects.filter(hospital = hos)
    patients = Patient.objects.filter(hospital = hos)
    nurses = Nurse.objects.filter(hospital = hos)
    hours = Hours.objects.filter(hospital = hos)
    return render_to_response('dashboard/hospital.html', {'type':get_user_type(request.user), 'hospital':hos, 'hours':hours, 'doctors':doctors, 'nurses':nurses, 'patients':patients}, context_instance=RequestContext(request))
	
# gets all the logged in users
def get_all_logged_in_users():
    # Query all non-expired sessions
    sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)

# gets all the upcoming appointments for a given user
def upcoming(user):
    appts = []
    type = get_user_type(user)
    if(type == "Patient"):
        for obj in Appointment.objects.filter(patient=get_user_object(user)):
            if(obj.date.date() in get_week(datetime.date.today())):
                appts.append(obj)
    elif(type == "Doctor"):
        for obj in Appointment.objects.filter(doctor=get_user_object(user)):
            if(obj.date.date() in get_week(datetime.date.today())):
                appts.append(obj)
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

# the list of admin users
@user_passes_test(admin_check)
def admin_list(request):
    admins = User.objects.filter(is_superuser=True)
    return render_to_response('dashboard/admin_list.html', {'type':"Admin", 'admin_list':admins}, context_instance=RequestContext(request))

# the list of a doctors patients	
def patients_list(request):
    u_type = get_user_type(request.user)
        
    if(u_type == "Doctor"):
        patients = Patient.objects.filter(doctor=Doctor.objects.filter(user=request.user))
    else:
        patients = Patient.objects.filter(nurse=Nurse.objects.filter(user=request.user))
    
    return render_to_response('dashboard/patient_list.html', {'type':get_user_type(request.user), 'patient_list':patients}, context_instance=RequestContext(request))

# the view that creates the profile page for the given id
@login_required(login_url='/login/')       
def user_view(request, name):
    user = User.objects.get(username=name)
    user_profile = get_user_object(user)
    can_edit = False
    can_delete = False
    tests = None
    if(get_user_type(user) == "Patient"):
        tests = Test.objects.filter(patient=user_profile)
    if(user_profile is not None and user_profile.hospital is None and request.user.is_staff and not request.user.is_superuser):
        button_text = "Admit"
    elif(user_profile is not None and user_profile.hospital is not None and (get_user_type(request.user) == "Doctor")):
        button_text = "Transfer"
        viewer = get_user_object(request.user)
        if(viewer is not None and user_profile.hospital == viewer.hospital):
            button_text = "Discharge"
    else:
        button_text = None
	
    if(user is request.user or request.user.is_superuser or get_user_type(request.user) is "Doctor"):
        can_edit = True
        if(request.user.is_superuser):
            can_delete = True
            
    return render_to_response('dashboard/profile.html', {'user':user, 'patient':user_profile, 'tests':tests, 'u_type':get_user_type(user), 'type':get_user_type(request.user), 'edit':can_edit, 'delete':can_delete,  'button_text':button_text}, context_instance=RequestContext(request))

# the view that creates the edit profile page for the given id.
@login_required(login_url='/login/')
@user_passes_test(edit_check)
def edit_user(request, name, template_name='dashboard/edit.html'):
    user = User.objects.get(username=name)
    user_profile = get_user_object(user)
    type = get_user_type(user)
    if(get_user_type(request.user) is "Doctor"):
        template_name='dashboard/med_edit.html'
        if request.method == 'POST':
            data = request.POST.copy()
            form = MedInfoForm(data, user = user_profile)
            if form.is_valid():
                form.save()
                Entry.objects.create_entry(request.user, 'updated_user_med_info: ' + user.username, datetime.datetime.now())
                return HttpResponseRedirect('/user/' + str(user))
        else:
            form = MedInfoForm(user = user_profile)
    else:
        if request.method == 'POST':
            data = request.POST.copy()
            data['username'] = user.username
            data['last_login'] = user.last_login
            data['date_joined'] = user.date_joined
            data['password'] = user.password
            data['is_staff'] = user.is_staff
            data['is_superuser'] = user.is_superuser
            form = UpdateUserForm(data, request.FILES, instance=user, editor=request.user)
            if form.is_valid():
                form.save()
                try:
                    if (type is 'Patient' and request.FILES['docfile']):
                        upload_info(request, user)
                except:
                    t = True
                Entry.objects.create_entry(request.user, 'updated_user: ' + user.username, datetime.datetime.now())
                return HttpResponseRedirect('/user/' + str(user))
        else:
            form = UpdateUserForm(instance=user)
    return render_to_response(template_name, {'viewer':request.user, 'user': user, 'patient':user_profile, 'form':form, 'u_type':get_user_type(user), 'type':get_user_type(request.user)}, context_instance=RequestContext(request))

# creates the profile page for the logged in user
@login_required(login_url='/login/')
def profile(request):
    user_profile = get_user_object(request.user)
    tests = None
    if(get_user_type(request.user) == "Patient"):
        tests = Test.objects.filter(patient=user_profile)
    return render_to_response('dashboard/profile.html', {'user': request.user, 'patient':user_profile, 'tests':tests, 'type':get_user_type(request.user), 'u_type':get_user_type(request.user), 'edit':True}, context_instance=RequestContext(request))

# creates the edit profile page for the logged in user
@login_required(login_url='/login/')
def edit_profile(request, template_name='dashboard/edit.html'):
    user_profile = get_user_object(request.user)
    type = get_user_type(request.user)
    
    if request.method == 'POST':
        data = request.POST.copy()
        data['username'] = request.user.username
        data['last_login'] = request.user.last_login
        data['date_joined'] = request.user.date_joined
        data['password'] = request.user.password
        data['is_staff'] = request.user.is_staff
        data['is_superuser'] = request.user.is_superuser
        form = UpdateUserForm(data, instance=request.user, editor=request.user)
        if form.is_valid():
            form.save()
            try:
                if (type is 'Patient' and request.FILES['docfile']):
                    upload_info(request, request.user)
            except:
                t = True
            Entry.objects.create_entry(request.user, 'user_updated_self', datetime.datetime.now())
            return HttpResponseRedirect('/profile/')
    else:
        form = UpdateUserForm(instance=request.user, editor=request.user)
    return render_to_response(template_name, {'viewer': request.user, 'user': request.user, 'patient':user_profile,'form':form, 'type':type, 'u_type':type}, context_instance=RequestContext(request))

def view_stats(request):
    hospitals = Hospital.objects.all()
    patient_count = []
    nurse_count = []
    doctor_count = []
    prep_count = []
    for hos in hospitals:
        prep = Prescription.objects.filter(hospital=hos)
        nurses = Nurse.objects.filter(hospital=hos)
        doctors = Doctor.objects.filter(hospital=hos)
        plist = Patient.objects.filter(hospital=hos)
        doctor_count.append(len(doctors))
        nurse_count.append(len(nurses))
        patient_count.append(len(plist))
        prep_count.append(len(prep))

    label = ["Doctors", "Nurses", "Patients", "Admins"]
    counts = [Doctor.objects.all().count(), Nurse.objects.all().count(), Patient.objects.all().count(), User.objects.filter(is_superuser=True).count()]
    tot = zip(label, counts)

    total_prep = zip(hospitals, prep_count)
    list = zip(hospitals, doctor_count, nurse_count, patient_count)
    return render_to_response('dashboard/statistics.html', {'type': get_user_type(request.user), 'total_users': User.objects.all().count(), 'tot':tot, 'prep':total_prep, 'hospitals': list, 'patient_count': patient_count}, context_instance=RequestContext(request))

def upload_info(request, name):
    user = User.objects.filter(username = name)[0]
    patient = get_user_object(user)
    test_results = Test.objects.filter(patient = patient)
    #file = request.FILES['docfile'].file
    file = TextIOWrapper(request.FILES['docfile'].file, encoding=request.encoding)
    for row in csv.reader(file):
        if row[0] == "PN":
            user.first_name = row[1]
            user.last_name = row[2]
        elif row[0] == "PE":
            user.email = row[1]
            patient.address = row[2]
            patient.phone_number = row[3]
            patient.insurance_id = row[4]
        elif  row[0] == "PD":
            if User.objects.filter(username = row[1]):
                patient.doctor = get_user_object(User.objects.filter(username = row[1])[0])
            if User.objects.filter(username = row[2]):
                patient.nurse = get_user_object(User.objects.filter(username = row[2])[0])
            patient.pref_hospital = Hospital.objects.filter(name = row[3])[0]
        elif row[0] == "PICE":
            patient.ice_name = row[1]
            patient.ice_phone = row[2]
        elif row[0] == "PTR":
            num_tests = row[1]
        elif row[0] == "TR":
            doctor = None
            if User.objects.filter(username = row[3]):
                doctor = get_user_object(User.objects.filter(username = row[3])[0])
            if(Test.objects.filter(name=row[1], notes=row[4], patient=patient, doctor=doctor, date=row[5]).count() == 0):
                test = Test.objects.create_test(row[1], row[4], None, patient, doctor, row[5])
                test.released = True
                test.save()
    user.save()
    patient.save()
    
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
