from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from WebAPI.choices import *
from datetime import datetime

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
    short_name = models.CharField(max_length=30, null = True, blank = True)
    owner = models.ForeignKey(User)
    visibility = models.BooleanField(default = False) #True for a public project, false for a private

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.short_name:
            self.short_name = self.name[0:2].upper()
        super(Project, self).save(*args, **kwargs)

class Board(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    default = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=40)

class State(models.Model):
    name = models.CharField(max_length=30)
    short_name = models.CharField(max_length = 5)
    order = models.IntegerField()
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True, blank=True, null = True)
    reset_password_hash = models.CharField(max_length = 50, blank = True, null=True)

    def __str__(self):
        return self.user.username

class Ticket(models.Model):
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=30, blank = True, null = True)
    description = models.TextField(default = "")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now = True)
    created_on = models.DateTimeField(auto_now_add=datetime.now())

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

    def save(self, *args, **kwargs):
        super(Ticket, self).save(*args, **kwargs)
        if not self.short_name:
            self.short_name = self.project.short_name + str(self.id)
            self.save()

class Invitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.EmailField()
    invitor = models.ForeignKey(User)
    issued = models.DateTimeField(auto_now_add=True, blank=True, null = True)

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(
        max_length = 10,
        choices = ACTIVITY_CHOICES,
        default = ACTIVITY_CHOICES[0][0],
    )

    item = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Board)
def create_states_for_board(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.default == False:
            default_board = Board.objects.get(project = instance.project, default=True)
            states = State.objects.filter(board = default_board)
            for state in states:
                state.pk = None
                state.board = instance
                state.save()



@receiver(post_save, sender=Project)
def create_default_board_for_project(sender, instance=None, created=False, **kwargs):
    if created:
        board = Board(owner=instance.owner, default=True, project=instance, title=instance.name)
        board.save()
        count = 1
        for k, v in STATE_CHOICES:
            state = State(name = v, short_name = k, order = count, board = board)
            state.save()
            count += 1
