from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from monitoring.models import *
from monitoring.swagger_schema import *
from monitoring.tests.common import CommonMethods

import math

class AssetViewSetTests(APITestCase, CommonMethods):
    def create_asset(self, author: User, access_cred: AccessCredential = None, cnt: int = 10) -> None:
        for i in range(cnt):
            q = Asset(author=author, name=f'{author.username}test{str(i)}',
                      ip='1.1.1.1'+str(i), port=22,
                      access_credential=access_cred, asset_type='linux')
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
        
        User.objects.create_user(
            username='test2', password='password', email='admin@myproject.com')
        self.test_user2 = User.objects.get(username='test2')

        self.cred = AccessCredential(
            author=self.super_user, name=f'{self.super_user.username}-id-password',
            access_type=AccessTypeChoices.ssh_password,
            username='root', password='qwer1234')
        self.cred.save()

        self.client.force_login(self.super_user)

    def tearDown(self):
        self.client.logout()
        self.connect_signal()
        return super().tearDown()

    def test_asset_list_get(self):
        url = reverse('monitoring:asset-list')
        response = self.client.get(url + '?ordering=-create_date')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_asset_list_get_unauthorized(self):
        self.client.logout()
        url = reverse('monitoring:asset-list')
        response = self.client.get(url + '?ordering=-create_date')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_list_get_pagination(self):
        asset_cnt = 50
        page_size = 10
        self.create_asset(self.super_user, self.cred, asset_cnt)
        url = reverse('monitoring:asset-list')
        response = self.client.get(url + '?ordering=-create_date')
        data = response.json()
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['total_pages'], math.ceil(asset_cnt/page_size))

    def test_asset_create_post(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '127.0.0.1',
            'port': 22,
            'asset_type': 'linux',
            'access_credential': self.cred.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_asset_create_post_without_permission(self):
        self.client.logout()
        self.client.force_login(self.test_user)
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '127.0.0.1',
            'port': 22,
            'asset_type': 'linux',
            'access_credential': self.cred.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_create_post_invalid_ip(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': 'qwer',
            'port': 22,
            'access_credential': self.cred.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_create_post_invalid_port(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '1.1.1.1',
            'port': 999999,
            'access_credential': self.cred.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_create_post_invalid_asset_type(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '1.1.1.1',
            'port': 22,
            'asset_type': 'qwer',
            'access_credential': self.cred.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_delete_bulk_delete(self):
        asset_cnt = 10
        delete_cnt = 5
        self.create_asset(self.super_user, self.cred, asset_cnt)
        asset_ids = [asset['id'] for asset in Asset.objects.all().values('id')]
        data = {
            'ids[]': asset_ids[:delete_cnt]
        }
        url = reverse('monitoring:asset-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.all().count(), asset_cnt - delete_cnt)

    def test_asset_delete_bulk_delete_not_author(self):
        self.client.logout()
        self.client.force_login(self.test_user)
        asset_cnt = 10
        delete_cnt = 5
        self.create_asset(self.super_user, self.cred, asset_cnt)
        asset_ids = [asset['id'] for asset in Asset.objects.all().values('id')]
        data = {
            'ids[]': asset_ids[:delete_cnt]
        }
        url = reverse('monitoring:asset-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Asset.objects.all().count(), asset_cnt)

    def test_asset_update_put(self):
        self.create_asset(self.super_user, self.cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'author': asset.author.id, 'name': asset.name,
                'ip': '2.2.2.2', 'port': 33, 'asset_type': 'linux',
                'access_credential': asset.access_credential.id, 'note': ''}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_asset_update_put_not_author(self):
        self.client.logout()
        self.client.force_login(self.test_user2)
        self.create_asset(self.test_user, self.cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'author': asset.author.id,'name': asset.name,
                'ip': '2.2.2.2', 'port': 33, 'asset_type': 'linux',
                'access_credential': asset.access_credential.id, 'note': ''}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_asset_update_put_not_author_but_change_author(self):
        self.client.logout()
        self.client.force_login(self.test_user2)
        self.create_asset(self.test_user, self.cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'author': self.test_user2.id, 'name': asset.name,
                'ip': '2.2.2.2', 'port': 33, 'asset_type': 'linux',
                'access_credential': asset.access_credential.id, 'note': ''}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_asset_update_put_not_changed_create_date(self):
        self.create_asset(self.super_user, self.cred, 1)
        asset = Asset.objects.all().first()
        old_date = asset.create_date
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'author': asset.author.id, 'name': asset.name,
                'ip': '2.2.2.2', 'port': 33, 'asset_type': 'linux',
                'access_credential': asset.access_credential.id, 'note': ''}
        response = self.client.put(url, data=data)
        new_date = Asset.objects.all().first().create_date
        self.assertEqual(old_date, new_date)

    def test_asset_partial_update_patch(self):
        self.create_asset(self.super_user, self.cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'author': asset.author.id, 'name': 'test'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
