from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from monitoring.models import *
from monitoring.tests.common import CommonMethods

import math


class AccessCredentialViewSetTests(APITestCase, CommonMethods):
    def create_access_credential(self, user: User, cnt: int = 10):
        for i in range(cnt):
            q = AccessCredential(user=user, name=f'{user.username}test{str(i)}',
                                 access_type=AccessTypeChoices.ssh_password,
                                 username='root', password='qwer1234')
            q.save()

    def setUp(self):
        super().setUp()
        self.disconnect_signal()
        User = get_user_model()
        User.objects.create_superuser(
            username='admin', password='password', email='admin@myproject.com')
        self.super_user = User.objects.get(username='admin')
        User.objects.create_user(
            username='test', password='password', email='admin@myproject.com')
        self.test_user = User.objects.get(username='test')
        self.client.force_login(self.super_user)

    def tearDown(self):
        self.client.logout()
        self.connect_signal()
        super().tearDown()

    def test_accesscredential_list_get(self):
        url = reverse('monitoring:accesscredential-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_accesscredential_list_get_unauthorized(self):
        self.client.logout()
        url = reverse('monitoring:accesscredential-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_list_get_pagination(self):
        cred_cnt = 50
        page_size = 10
        self.create_access_credential(self.super_user, cred_cnt)
        url = reverse('monitoring:accesscredential-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['total_pages'], math.ceil(cred_cnt/page_size))

    def test_asset_list_get_only_mine(self):
        cred_cnt = 10
        self.create_access_credential(self.test_user, cred_cnt)
        url = reverse('monitoring:accesscredential-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['total_items'], 0)

    def test_accesscredential_create_post(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_password.value,
            'username': 'root',
            'password': 'passwd'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accesscredential_create_post_password_empty(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_password.value,
            'username': '',
            'password': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_password_secret(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_password.value,
            'secret': 'asdfasdf'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_password_none(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_password.value,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_private_key.value,
            'secret': 'qwerqwer'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accesscredential_create_post_private_key_empty(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_private_key.value,
            'secret': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key_password(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_private_key.value,
            'username': 'root',
            'password': 'passwd'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key_none(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessTypeChoices.ssh_private_key.value,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_invalid_access_type(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': 'qwer',
            'username': 'root',
            'password': 'passwd'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_delete_bulk_delete(self):
        cred_cnt = 10
        delete_cnt = 5
        self.create_access_credential(self.super_user, cred_cnt)
        url = reverse('monitoring:accesscredential-delete-bulk')
        cred_ids = [cred['id']
                    for cred in AccessCredential.objects.all().values('id')]
        data = {
            'ids[]': cred_ids[:delete_cnt]
        }
        response = self.client.delete(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessCredential.objects.all().count(),
                         cred_cnt - delete_cnt)

    def test_accesscredential_delete_bulk_delete_cannot_delete_others(self):
        cred_cnt = 10
        delete_cnt = 5
        self.create_access_credential(self.test_user, cred_cnt)
        url = reverse('monitoring:accesscredential-delete-bulk')
        cred_ids = [cred['id']
                    for cred in AccessCredential.objects.all().values('id')]
        data = {
            'ids[]': cred_ids[:delete_cnt]
        }
        response = self.client.delete(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessCredential.objects.all().count(), cred_cnt)

    def test_accesscredential_list_simple_get(self):
        cred_cnt = 30
        self.create_access_credential(self.super_user, cred_cnt)
        url = reverse('monitoring:accesscredential-list-simple')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), cred_cnt)
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('access_type', data[0])
        self.assertNotIn('username', data[0])
        self.assertNotIn('password', data[0])
        self.assertNotIn('secret', data[0])

    def test_accesscredential_update_put_not_changed_create_date(self):
        self.create_access_credential(self.super_user, 1)
        cred = AccessCredential.objects.all().first()
        old_date = cred.create_date
        cred.name = 'testname'
        cred.save()
        new_date = AccessCredential.objects.all().first().create_date
        self.assertEqual(old_date, new_date)
