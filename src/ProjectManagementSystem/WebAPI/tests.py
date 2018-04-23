# from django.test import TestCase
# from rest_framework.test import force_authenticate, APIRequestFactory, APITestCase
# from django.urls import reverse
# from rest_framework import status
# from WebAPI.models import *
#
# factory = APIRequestFactory()
# request. = factory.post('/notes/', {'title' : 'new idea'}, format='json')
#
# class AccountTests(APITestCase):
#     def test_create_account(self):
#         url = reverse('users/')
#         data = {
#                 'name' : 'DabApps'
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Account.objects.count(), 1)
#         self.assertEqual(Account.objects.get().name, 'DabApps')
#
#     def test_delete_account(self):
#         url = reverse('users/')
#         data = {
#                 'name' : 'DabApps'
#
#         }
#         response = self.client.delete(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Account.objects.count(), 1)
#         self.assertEqual(Account.objects.get().name, 'DabApps')
#
#     def test_update_account(self):
#         url = reverse('users/')
#         data = {
#                 'name' : 'DabApps'
#
#         }
#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Account.objects.count(), 1)
#         self.assertEqual(Account.objects.get().name, 'DabApps')
