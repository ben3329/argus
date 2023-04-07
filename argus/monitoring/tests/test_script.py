from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import *
from ..api_params import *
import math
from typing import Union
from datetime import datetime
import secrets


class ScriptViewSetTests(APITestCase):
    def create_script(self, user: User, authority: Union[AuthorityChoices, str], cnt: int = 10) -> None:
        for i in range(cnt):
            q = Script(user=user, name=secrets.token_hex(5), language=LanguageChoices.shell,
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
        q = Script(user=self.super_user, name='2', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = Script(user=self.super_user, name='1', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = Script(user=self.super_user, name='0', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = Script(user=self.test_user, name='5', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = Script(user=self.test_user, name='4', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        q = Script(user=self.test_user, name='3', language=LanguageChoices.shell,
                   code='ls', authority=AuthorityChoices.public, output_type=OutputTypeChoices.none)
        q.save()
        obj = Script.objects.get(name='0')
        obj.update_date = datetime.now()
        obj.save()
        obj = Script.objects.get(name='3')
        obj.update_date = datetime.now()
        obj.save()

        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        for idx, d in enumerate(data['results']):
            self.assertEqual(d['name'], str(idx))

    def test_script_list_get_match_swagger(self):
        cnt = 1
        self.create_script(
            self.super_user, AuthorityChoices.private.value, cnt)
        url = reverse('monitoring:script-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(
            script_list_api_response_properties.keys(), data['results'][0].keys())

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
