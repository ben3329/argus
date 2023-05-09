from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import *
from ..swagger_schema import *
import math
from typing import Union
from datetime import datetime
import secrets


class ScriptViewSetTests(APITestCase):
    def create_script(self, user: User, authority: Union[AuthorityChoices, str], cnt: int = 10) -> None:
        for i in range(cnt):
            q = UserDefinedScript(user=user, name=secrets.token_hex(5), language=LanguageChoices.shell,
                       code='ls', authority=authority, output_type=OutputTypeChoices.none)
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

    def test_script_list_get(self):
        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_list_get_unauthorized(self):
        self.client.logout()
        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_script_list_get_public(self):
        cnt = 1
        self.create_script(self.test_user, AuthorityChoices.private.value, cnt)
        self.create_script(self.test_user, AuthorityChoices.public.value, cnt)
        self.create_script(
            self.super_user, AuthorityChoices.private.value, cnt)
        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['total_items'], cnt*2)

    def test_script_list_get_order_mine_others(self):
        cnt = 1
        self.create_script(self.test_user, AuthorityChoices.private.value, cnt)
        self.create_script(self.test_user, AuthorityChoices.public.value, cnt)
        self.create_script(
            self.super_user, AuthorityChoices.private.value, cnt)

        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        for idx, d in enumerate(data['results']):
            if idx < cnt:
                self.assertEqual(d['user'], self.super_user.id)
            else:
                self.assertEqual(d['user'], self.test_user.id)

    def test_script_list_get_order_by_update_date(self):
        q = UserDefinedScript(user=self.super_user, name='2', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = UserDefinedScript(user=self.super_user, name='1', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = UserDefinedScript(user=self.super_user, name='0', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = UserDefinedScript(user=self.test_user, name='5', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = UserDefinedScript(user=self.test_user, name='4', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = UserDefinedScript(user=self.test_user, name='3', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        obj = UserDefinedScript.objects.get(name='0')
        obj.update_date = datetime.now()
        obj.save()
        obj = UserDefinedScript.objects.get(name='3')
        obj.update_date = datetime.now()
        obj.save()

        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        for idx, d in enumerate(data['results']):
            self.assertEqual(d['name'], str(idx))

    def test_script_list_get_pagination(self):
        cnt = 50
        page_size = 10
        self.create_script(
            self.super_user, AuthorityChoices.private.value, cnt)
        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['total_pages'], math.ceil(cnt/page_size))

    def test_script_retrieve_get(self):
        self.create_script(self.super_user, AuthorityChoices.private.value, 1)
        script = UserDefinedScript.objects.all().first()
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_retrieve_get_others_private(self):
        self.create_script(self.test_user, AuthorityChoices.private.value, 1)
        script = UserDefinedScript.objects.all().first()
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_script_retrieve_get_others_public(self):
        self.create_script(self.test_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_retrieve_get_not_exist(self):
        url = reverse('monitoring:script-detail', kwargs={'pk': 5})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_script_create_post(self):
        url = reverse('monitoring:script-list')
        data = {
            'name': 'test script',
            'language': LanguageChoices.shell.value,
            'code': 'ls',
            'authority': AuthorityChoices.public.value,
            'output_type': OutputTypeChoices.csv.value,
            'note': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_script_create_post_exist_name(self):
        url = reverse('monitoring:script-list')
        data = {
            'name': 'test script',
            'language': LanguageChoices.shell.value,
            'code': 'ls',
            'authority': AuthorityChoices.public.value,
            'output_type': OutputTypeChoices.csv.value,
            'note': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.json()), ['name'])

    def test_script_create_post_invalid_language(self):
        url = reverse('monitoring:script-list')
        data = {
            'name': 'test script',
            'language': 'asdfad',
            'code': 'ls',
            'authority': AuthorityChoices.public.value,
            'output_type': OutputTypeChoices.csv.value,
            'note': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.json()), ['language'])

    def test_script_create_post_invalid_authority(self):
        url = reverse('monitoring:script-list')
        data = {
            'name': 'test script',
            'language': LanguageChoices.shell.value,
            'code': 'ls',
            'authority': 'qwerqwe',
            'output_type': OutputTypeChoices.csv.value,
            'note': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.json()), ['authority'])

    def test_script_create_post_invalid_authority(self):
        url = reverse('monitoring:script-list')
        data = {
            'name': 'test script',
            'language': LanguageChoices.shell.value,
            'code': 'ls',
            'authority': AuthorityChoices.public.value,
            'output_type': 'qwerqwer',
            'note': ''
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(list(response.json()), ['output_type'])

    def test_script_delete_bulk_delete(self):
        cnt = 10
        delete_cnt = 5
        self.create_script(self.super_user, AuthorityChoices.public.value, cnt)
        ids = [script['id'] for script in UserDefinedScript.objects.all().values('id')]
        data = {
            'ids[]': ids[:delete_cnt]
        }
        url = reverse('monitoring:script-delete-bulk')
        response = self.client.delete(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserDefinedScript.objects.all().count(), cnt - delete_cnt)

    def test_script_update_put(self):
        self.create_script(self.super_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        data = {'user': self.super_user, 'name': script.name,
                'language': script.language, 'code': script.code,
                'authority': AuthorityChoices.private.value,
                'output_type': script.output_type,
                'note': ''}
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_script_update_put_update_update_date(self):
        self.create_script(self.super_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        old_date = script.update_date
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        data = {'user': self.super_user, 'name': script.name,
                'language': script.language, 'code': script.code,
                'authority': AuthorityChoices.private.value,
                'output_type': script.output_type,
                'note': ''}
        response = self.client.put(url, data=data)
        new_date = UserDefinedScript.objects.all().first().update_date
        self.assertNotEqual(old_date, new_date)

    def test_script_update_put_not_changed_create_date(self):
        self.create_script(self.super_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        old_date = script.create_date
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        data = {'user': self.super_user, 'name': script.name,
                'language': script.language, 'code': script.code,
                'authority': AuthorityChoices.private.value,
                'output_type': script.output_type,
                'note': ''}
        response = self.client.put(url, data=data)
        new_date = UserDefinedScript.objects.all().first().create_date
        self.assertEqual(old_date, new_date)

    def test_script_update_put_update_revision(self):
        self.create_script(self.super_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        self.assertEqual(script.revision, 1)
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        data = {'user': self.super_user, 'name': script.name,
                'language': script.language, 'code': script.code,
                'authority': AuthorityChoices.private.value,
                'output_type': script.output_type,
                'note': ''}
        response = self.client.put(url, data=data)
        revision = UserDefinedScript.objects.all().first().revision
        self.assertEqual(revision, 2)

    def test_script_partial_update_patch(self):
        self.create_script(self.super_user, AuthorityChoices.public.value, 1)
        script = UserDefinedScript.objects.all().first()
        url = reverse('monitoring:script-detail', kwargs={'pk': script.id})
        data = {'name': 'test'}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
