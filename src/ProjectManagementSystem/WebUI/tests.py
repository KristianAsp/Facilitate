from django.test import TestCase, Client
from django.contrib.auth.models import User
from WebAPI.models import *
import unittest, re, pdb

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_register(self):
        response = self.client.post('/register/', {'username': 'john', 'email': 'kristian.aspevik@gmail.com', 'password' : 'hello', 'confirm_password' : 'hello'})
        print(response.status_code)

    def test_login(self):
        response = self.client.post('/login/', {'username': 'john', 'password': 'hello'})
        print(response.status_code)

def get_middleware_token(response):
    response_decoded = response.content.decode('utf-8')
    token = re.split('csrfmiddlewaretoken', response_decoded)[1].split('\'')[2]
    return token

class csrf_tests(TestCase):
    def setUp(self):
        self.client = Client()
        u = 'Kristian'
        p = "password123"

        user = User.objects.create(username=u)
        user.set_password(p)
        user.save()
        profile = Profile.objects.create(user = user)

    def test_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

        query = {
                'csrfmiddlewaretoken' : get_middleware_token(response),
                'username' : 'Kristian',
                'password' : 'password123',
        }

        response2 = self.client.post('/login/', query)
        self.assertEqual(response2.status_code, 302)

    def test_create_project(self):
        self.client.login(username='Kristian', password='password123')
        response = self.client.get('/project/new/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

        query = {
                'csrfmiddlewaretoken' : get_middleware_token(response),
                'public' : 'on',
                'name' : 'Final Year Project',
                'description' : 'A Final Year Project',
        }
        response = self.client.post('/project/new/', query)
        self.assertEqual(response.status_code, 302)

    def test_create_task(self):
        self.client.login(username='Kristian', password='password123')

        ####
        # Create a new project for the task to be stored in.
        ####
        response = self.client.get('/project/new/')
        query = {
                'csrfmiddlewaretoken' : get_middleware_token(response),
                'public' : 'on',
                'name' : 'Final Year Project',
                'description' : 'A Final Year Project',
        }
        response = self.client.post('/project/new/', query)

        response = self.client.get('/dashboard/tasks/new')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

        query = {
                'csrfmiddlewaretoken' : get_middleware_token(response),
                'name' : 'Write unittests for API',
                'priority' : '1',
                'description' : 'Each view in the API should have its own unittest',
                'type' : 'B',
        }
        response = self.client.post('/dashboard/tasks/new', query)
        self.assertEqual(response.status_code, 200)
