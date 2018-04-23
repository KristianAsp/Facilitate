from django.test import TestCase
from WebAPI.models import *


class ProjectTest(TestCase):
    """ Test module for Project model """

    def setUp(self):
        user = User.objects.create(username='John', email="john.doe@gmail.com")
        user.set_password("password123")

        project = Project.objects.create(name='Final Year Project', short_name = "FI", owner=User, visibility=False, description="A project")

    def test_project_name_string(self):
        project = Project.objects.get(name='Final Year Project')
        self.assertEqual(project, "Final Year Project")
        self.assertEqual(Project.objects.all().count(), 1)

class AccountTest(TestCase):
    user = None
    def setUp(self):
        self.user = User.objects.create(username='John', email='john.doe@gmail.com')
        user.set_password('password123')

    def test_authentication_token(self):
