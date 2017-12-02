from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User



class Project(models.Model):
    name = models.CharField(max_length=30)
    owner = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project)

    def __str__(self):
        return self.user.username


class Ticket(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

    TYPE_CHOICES = (
        ('S', 'Story'),
        ('E', 'Epic'),
        ('B', 'Bug'),
        ('T', 'Task'),
    )

    type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='T'
    )

    PRIORITY_CHOICES = (
        ('C', 'Critical'),
        ('H', 'High'),
        ('M', 'Medium'),
        ('L', 'Low'),
    )

    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default='M',
    )

    assigned_to = models.ForeignKey(User)
    state = models.CharField(max_length=20)

    def __str__(self):
        return self.name

#####
# use a signal to detect when a user has been created. When it is created, a unique Token should be allocated to this user
# for authentication purposes whenever they use the API.
#####
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_authentication_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
