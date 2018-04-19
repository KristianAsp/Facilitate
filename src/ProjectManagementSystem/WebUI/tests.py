from django.test import TestCase, Client
import unittest

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_register(self):
        response = self.client.post('/register/', {'username': 'john', : 'smith', 'password' : 'hello', 'confirm_password' : 'hello'})
        print(response.status_code)

    def test_login(self):
        response = self.client.post('/login/', {'username': 'john', 'password': 'smith'})
        print(response.status_code)
