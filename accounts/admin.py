from django.contrib import admin
 
from .models import Patient, Doctor, Nurse, Hospital, Hours

# added all of the models to the admin site
admin.site.register(Patient)
 
admin.site.register(Doctor)
 
admin.site.register(Nurse)

admin.site.register(Hospital)

admin.site.register(Hours)


