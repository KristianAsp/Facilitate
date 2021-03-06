from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from WebAPI.choices import *
from datetime import datetime, date


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
    description = models.TextField(blank=True, null=True)

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
    order = models.IntegerField(blank = True, null = True, default = -1)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True, blank=True, null = True)
    reset_password_hash = models.CharField(max_length = 50, blank = True, null=True)

class Ticket(models.Model):
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=30, blank = True, null = True)
    description = models.TextField(blank = True, null = True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now = True)
    created_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="ticket_created_by")
    associated_users = models.ManyToManyField(User, related_name="associated_users")

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

    assigned_to = models.ForeignKey(User, blank = True, null = True, related_name="ticket_assigned_to")
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

        if self.state == 'C' and not self.completed_on:
            self.completed_on = datetime.now()
            self.save()

        elif self.state != "C" and self.completed_on:
            self.completed_on = None
            self.save()

class Invitation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.EmailField()
    invitor = models.ForeignKey(User)
    issued = models.DateTimeField(auto_now_add=True, blank=True, null = True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_on',)

def project_directory_path(instance, filename):
    return settings.MEDIA_ROOT + 'documents/project_{0}/{1}'.format(instance.project.id, filename)

class Event(models.Model):
    event_title = models.CharField(max_length=255, default="Untitled")
    type = models.CharField(
        max_length=1,
        choices=EVENT_TYPE_CHOICES,
        default=EVENT_TYPE_CHOICES[0][0]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    added_by = models.ForeignKey(User)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Document(models.Model):
    document_name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=project_directory_path, max_length=700)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    associated_event = models.ForeignKey(Event, blank=True, null=True)

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

@receiver(post_save, sender=Ticket)
def add_creator_to_associated_users(sender, instance=None, created=False, **kwargs):
    if created:
        instance.associated_users.add(instance.created_by)
