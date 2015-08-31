from django.conf.urls import patterns, include, url

from django.contrib import admin
from accounts.forms import PatientForm
from django.views.generic.edit import CreateView
from django.conf.urls.static import static
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # the login views, uses the default django login views with our custom template
    url(r'^$', 'accounts.views.custom_login', {'template_name': 'accounts/login.html'}),
    url(r'^login/$', 'accounts.views.custom_login', {'template_name': 'accounts/login.html'}),
    # the logout view, uses the default django logout view with our custom template
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'accounts/logout.html'}),
    # the profile view in dashboard
    url(r'^profile/$', 'dashboard.views.profile'),
    # the patient_list view in dashboard
    url(r'^patients/$', 'dashboard.views.patients_list'),
    # the online user list view in dashboard
    url(r'^users/$', 'dashboard.views.user_list'),
    # the admin list view in dashboard
    url(r'^admins/$', 'dashboard.views.admin_list'),
    # the profile edit view in dashboard
    url(r'^profile/edit/$', 'dashboard.views.edit_profile'),
    # the register doctor view in accounts
    url(r'^user/doctor/add/$', 'accounts.views.register_doctor'),
    # the register patient view in accounts
    url(r'^user/patient/add/$', 'accounts.views.register_patient'),

    url(r'^user/patient/admit/(?P<pk>\w+)/$', 'dashboard.views.admit_patient', name='admit_patient'),
    # the register nurse view in accounts
    url(r'^user/nurse/add/$', 'accounts.views.register_nurse'),
    # the register admin view in accounts
    url(r'^user/admin/add/$', 'accounts.views.register_admin'),

    url(r'^test/release/(?P<pk>\w+)/$', 'tests.views.release', name='test_rel'),
    url(r'^user/(?P<name>[a-zA-Z ].*)/test/new/$', 'tests.views.add', name='new_test'),
    url(r'^user/(?P<name>[a-zA-Z ].*)/test/(?P<pk>\w+)/$', 'tests.views.view', name='test'),
    url(r'^user/(?P<name>[a-zA-Z ].*)/test/(?P<pk>\w+)/edit/$', 'tests.views.edit', name='test_edit'),
    url(r'^user/(?P<name>[a-zA-Z ].*)/export/$', 'accounts.views.export_info', name='export'),
    # the edit user view in dashboard, the pk is what the id of the user you want to edit
    url(r'^user/(?P<name>[a-zA-Z ].*)/edit/$', 'dashboard.views.edit_user', name='user_edit'),
    # the user view in dashboard, the pk is what the id of the user you want to view
    url(r'^user/(?P<name>[a-zA-Z ].*)/$', 'dashboard.views.user_view', name='user'),
    # the initial register patient view on the login screen. Uses a builtin django thing to inflate a custom template with a specified form in the background
    url('^register/', CreateView.as_view(template_name='accounts/register.html', form_class=PatientForm, success_url='/home/')),

    url(r'^messages/$', 'messaging.views.main'),

    url(r'^messages/compose/$', 'messaging.views.compose'),
    url(r'^messages/compose/(?P<user>[a-zA-Z ].*)/$', 'messaging.views.compose', name='compose'),
    url(r'^messages/reply/(?P<pk>\w+)/$', 'messaging.views.compose', name='reply'),

    url(r'^messages/(?P<pk>\w+)/$', 'messaging.views.viewMessage', name='message'),
       
    url(r'^hospitals/$', 'dashboard.views.hos_list'),
    url(r'^hospitals/add/$', 'dashboard.views.add_hospital'),
    url(r'^hospitals/(?P<name>[a-zA-Z ].*)/$', 'dashboard.views.hos_view', name='hospitals'),

    # the home prescription list view
    url(r'^scripts/$', 'prescriptions.views.main'),
    # the add prescription view
    url(r'^scripts/add/$', 'prescriptions.views.add'),
    # the delete prescription view
    url(r'^scripts/delete/(?P<pk>\w+)/$', 'prescriptions.views.delete', name='rx_delete'),
    # the home dashboard view                   
    url(r'^home/$', 'dashboard.views.home'),
    # the home appointment calendar view
    url(r'^appt/$', 'appt_calendar.views.main'),
    # the edit appointment view
    url(r'^appt/edit/(?P<pk>\w+)/$', 'appt_calendar.views.edit', name='appt'),
    # the delete appointment view
    url(r'^appt/delete/(?P<pk>\w+)/$', 'appt_calendar.views.delete', name='appt_cancel'),
    # the add appointment view
    url(r'^appt/add/$', 'appt_calendar.views.add'),
    # the add appointment view for a specific patient
    url(r'^appt/add/(?P<pat>\w+)/$', 'appt_calendar.views.add', name="pat_appt"),
    url(r'^stats/$', 'dashboard.views.view_stats', name="statistics"),
    # the stuff for the admin site
    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
