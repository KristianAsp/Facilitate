from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from WebAPI.choices import *

#####
# use a signal to detect when a user has been created. When it is created, a unique Token should be allocated to this user
# for authentication purposes whenever they use the API.
#####
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_authentication_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Project(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User)
    visibility = models.BooleanField(default = False) #True for a public project, false for a private

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True, blank=True, null = True)

    def __str__(self):
        return self.user.username

class Ticket(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(default = "Hello")
    project = models.ForeignKey(Project)

    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0][0]
    )

    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_CHOICES[0][0],
    )

    assigned_to = models.ForeignKey(User, blank = True, null = True)
    state = models.CharField(
        max_length=5,
        choices=STATE_CHOICES,
        default=STATE_CHOICES[0][0],
    )

    def __str__(self):
        return self.name

class Invitation(models.Model):
    project = models.ForeignKey(Project)
    user = models.EmailField()
    invitor = models.ForeignKey(User)
    issued = models.DateTimeField(auto_now_add=True, blank=True, null = True)

class Activity(models.Model):
    user = models.ForeignKey(User)
