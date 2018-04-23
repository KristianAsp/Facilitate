from django.test import TestCase
from WebAPI.models import *
from django.contrib.auth.models import User


class ProjectTest(TestCase):
    """ Test module for Project model """

    def setUp(self):
        self.user = User.objects.create(username='John', email="john.doe@gmail.com")
        self.user.set_password("password123")

        self.project = Project.objects.create(name='Final Year Project', owner=self.user, visibility=False, description="A project")

    def test_project_name_string(self):
        project = Project.objects.get(name='Final Year Project')
        self.assertEqual(project.name, "Final Year Project")

    def test_project_count(self):
        self.assertEqual(Project.objects.all().count(), 1)

    ###
    # Project attribute short_name should be automatically generated based on the full Project name.
    ###
    def test_short_name(self):
        project = Project.objects.get(name='Final Year Project')
        self.assertEqual(project.short_name, 'FI')

    ###
    # A default board for the project should be created when a new project is created.
    ###
    def test_created_default_board(self):
        b = Board.objects.filter(project = self.project, default = True).count()
        self.assertEqual(b, 1)

    ###
    # When a user is deleted, all projects should be delete if said user is the owner.
    ###
    def test_cascade_on_delete(self):
        self.assertEqual(Project.objects.all().count(), 1)
        self.user.delete()
        self.assertEqual(Project.objects.all().count(), 0)


class AccountTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='John', email='john.doe@gmail.com')
        self.user.set_password('password123')

    ###
    # Test that an authentication token is automatically created when a new user is created
    ###
    def test_authentication_token(self):
        t = Token.objects.filter(user = self.user).count()
        self.assertEqual(t, 1)

class BoardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='John', email="john.doe@gmail.com")
        self.user.set_password("password123")

        self.project = Project.objects.create(name='Final Year Project', owner=self.user, visibility=False, description="A project")
    ###
    # Test that the default states from the default board is automatically copied over to a new non-default board
    ###
    def test_automatic_state_creation(self):
        b = Board.objects.create(owner = self.user, default = False, project = self.project, title='Copy of Default Board')
        statesCount = State.objects.filter(board = b).count()
        self.assertEqual(statesCount, 5)

    def test_cascade_on_delete_board(self):
        b = Board.objects.create(owner = self.user, default = False, project = self.project, title='Copy of Default Board')
        statesCount = State.objects.all().count()
        self.assertEqual(statesCount, 10) # 10 because the default board has 5 + the new board that has 5
        b.delete()
        statesCount = State.objects.all().count()
        self.assertEqual(statesCount, 5) # 5 because the default board has 5 and we're only deleting a copy

    def test_deleting_state_from_board(self):
        b = Board.objects.create(owner = self.user, default = False, project = self.project, title='Copy of Default Board')
        statesCount = State.objects.filter(board = b)
        self.assertEqual(len(statesCount), 5)
        statesCount[0].delete()
        statesCount = State.objects.filter(board = b)
        self.assertEqual(len(statesCount), 4)
