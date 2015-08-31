from django.db import models
from django.contrib.auth.models import User

#a class that facilitates creation of Entry objects
class EntryManager(models.Manager):
    def create_entry(self, user, action, date):
        entry = self.create(user = user, action = action, date = date)
        return entry

#an Entry in the logger records the user that performed the action,
#the type of action, and the date and time when the action occurred
class Entry(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    objects = EntryManager()
    class Meta:
        verbose_name = 'Entry'
    def __str__(self):
        return self.user.username

