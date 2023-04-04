from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import *
import math


class AssetViewSetTests(APITestCase):
    def create_asset(self, user: User, access_cred: AccessCredential = None, cnt: int = 10) -> None:
        for i in range(cnt):
            q = Asset(user=user, name=f'{user.username}test{str(i)}', ip='1.1.1.1'+str(i),
                      access_credential=access_cred)
            q.save()

    def setUp(self):
        User = get_user_model()

        User.objects.create_superuser(
            username='admin', password='password', email='admin@myproject.com')
        self.super_user = User.objects.get(username='admin')
        self.admin_cred = AccessCredential(
            user=self.super_user, name=f'{self.super_user.username}-id-password',
            access_type=AccessType.ssh_id_password,
            username='root', password='qwer1234')
        self.admin_cred.save()

        User.objects.create_user(
            username='test', password='password', email='admin@myproject.com')
        self.test_user = User.objects.get(username='test')
        self.test_cred = AccessCredential(
            user=self.test_user, name=f'{self.test_user.username}-id-password',
            access_type=AccessType.ssh_id_password,
            username='root', password='qwer1234')
        self.test_cred.save()

        self.client.force_login(self.super_user)
        return super().setUp()

    def tearDown(self):
        self.client.logout()
        return super().tearDown()

    def test_asset_list_get(self):
        url = reverse('monitoring:asset-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_asset_list_get_unauthorized(self):
        self.client.logout()
        url = reverse('monitoring:asset-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_asset_list_get_all_by_super_user(self):
        asset_cnt = 10
        self.create_asset(self.test_user, self.test_cred, asset_cnt)
        self.create_asset(self.super_user, self.admin_cred, asset_cnt)
        url = reverse('monitoring:asset-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['total_items'], asset_cnt*2)

    def test_asset_list_get_only_mine_by_normal_user(self):
        self.client.logout()
        self.client.force_login(self.test_user)
        asset_cnt = 10
        self.create_asset(self.test_user, self.test_cred, asset_cnt)
        self.create_asset(self.super_user, self.admin_cred, asset_cnt)
        url = reverse('monitoring:asset-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['total_items'], asset_cnt)

    def test_asset_list_get_pagination(self):
        asset_cnt = 50
        page_size = 10
        self.create_asset(self.super_user, self.admin_cred, asset_cnt)
        url = reverse('monitoring:asset-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['total_pages'], math.ceil(asset_cnt/page_size))

    def test_asset_create_post(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '127.0.0.1',
            'port': 22,
            'access_credential': self.admin_cred.id,
            'user': self.super_user
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_asset_create_post_use_others_cred(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '127.0.0.1',
            'port': 22,
            'access_credential': self.test_cred.id,
            'user': self.super_user
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_create_post_invalid_ip(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': 'qwer',
            'port': 22,
            'access_credential': self.test_cred.id,
            'user': self.super_user
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_create_post_invalid_port(self):
        url = reverse('monitoring:asset-list')
        data = {
            'name': 'test asset',
            'ip': '1.1.1.1',
            'port': 999999,
            'access_credential': self.test_cred.id,
            'user': self.super_user
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
            'access_credential': self.test_cred.id,
            'user': self.super_user
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_asset_delete_bulk_delete(self):
        asset_cnt = 10
        delete_cnt = 5
        self.create_asset(self.super_user, self.admin_cred, asset_cnt)
        asset_ids = [asset['id'] for asset in Asset.objects.all().values('id')]
        data = {
            'ids[]': asset_ids[:delete_cnt]
        }
        url = reverse('monitoring:asset-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.all().count(), asset_cnt - delete_cnt)

    def test_asset_delete_bulk_delete_others_by_super_user(self):
        asset_cnt = 10
        delete_cnt = 5
        self.create_asset(self.test_user, self.test_cred, asset_cnt)
        asset_ids = [asset['id'] for asset in Asset.objects.all().values('id')]
        data = {
            'ids[]': asset_ids[:delete_cnt]
        }
        url = reverse('monitoring:asset-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.all().count(), asset_cnt - delete_cnt)

    def test_asset_delete_bulk_delete_others_by_normal_user(self):
        self.client.logout()
        self.client.force_login(self.test_user)
        asset_cnt = 10
        delete_cnt = 5
        self.create_asset(self.super_user, self.admin_cred, asset_cnt)
        asset_ids = [asset['id'] for asset in Asset.objects.all().values('id')]
        data = {
            'ids[]': asset_ids[:delete_cnt]
        }
        url = reverse('monitoring:asset-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Asset.objects.all().count(), asset_cnt)

    def test_asset_update_put(self):
        self.create_asset(self.super_user, self.admin_cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'user': asset.user.id, 'name': asset.name,
                'ip': '2.2.2.2', 'port': 33, 'asset_type': 'linux',
                'access_credential': asset.access_credential.id, 'note': ''}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_asset_partial_update_patch(self):
        self.create_asset(self.super_user, self.admin_cred, 1)
        asset = Asset.objects.all().first()
        url = reverse('monitoring:asset-detail', kwargs={'pk': asset.id})
        data = {'id': asset.id, 'user': asset.user.id, 'name': 'test'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AccessCredentialViewSetTests(APITestCase):
    def create_access_credential(self, user: User, cnt: int = 10):
        for i in range(cnt):
            q = AccessCredential(user=user, name=f'{user.username}test{str(i)}',
                                 access_type=AccessType.ssh_id_password,
                                 username='root', password='qwer1234')
            q.save()

    def setUp(self):
        User = get_user_model()
        User.objects.create_superuser(
            username='admin', password='password', email='admin@myproject.com')
        self.super_user = User.objects.get(username='admin')
        User.objects.create_user(
            username='test', password='password', email='admin@myproject.com')
        self.test_user = User.objects.get(username='test')
        self.client.force_login(self.super_user)
        return super().setUp()

    def tearDown(self):
        self.client.logout()
        return super().tearDown()

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
            'access_type': AccessType.ssh_id_password.value,
            'username': 'root',
            'password': 'passwd'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accesscredential_create_post_id_password_empty(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_id_password.value,
            'username': '',
            'password': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_id_password_secret(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_id_password.value,
            'secret': 'asdfasdf'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_id_password_none(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_id_password.value,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_private_key.value,
            'secret': 'qwerqwer'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accesscredential_create_post_private_key_empty(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_private_key.value,
            'secret': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key_id_password(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_private_key.value,
            'username': 'root',
            'password': 'passwd'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accesscredential_create_post_private_key_none(self):
        url = reverse('monitoring:accesscredential-list')
        data = {
            'name': 'test',
            'access_type': AccessType.ssh_private_key.value,
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
