from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from django.contrib.auth import get_user_model

from monitoring.models import *
from monitoring.tests.common import CommonMethods

import json


class MonitorViewSetTests(APITestCase, CommonMethods):
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
        
        self.cred = AccessCredential(
            author=self.super_user, name=f'{self.super_user.username}-id-password',
            access_type=AccessTypeChoices.ssh_password,
            username='root', password='password')
        self.cred.save()
        self.asset = Asset(
            author=self.super_user, name='test_asset',
            ip='192.168.0.150', port=22, asset_type='linux',
            access_credential=self.cred)
        self.asset.save()
        self.user_defined_script = UserDefinedScript(
            author=self.super_user, name='test_script', language='bash',
            code='ls', output_type=OutputTypeChoices.none)
        self.user_defined_script.save()
        self.monitor = Monitor(
            name='test_monitor', asset=self.asset,
            scrape_category='linux_system_memory', scrape_fields=['used'],
            interval=1, report_list=["graph24", "diff"],
            report_time='0 8 * * *',
            author=self.super_user)
        self.monitor.save()

        self.client.force_login(self.super_user)

    def tearDown(self):
        self.client.logout()
        self.connect_signal()
        return super().tearDown()

    def test_monitor_list_get(self):
        url = reverse('monitoring:monitor-list')
        response = self.client.get(url + '?ordering=-create_date')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_monitor_list_get_unauthorized(self):
        self.client.logout()
        url = reverse('monitoring:monitor-list')
        response = self.client.get(url + '?ordering=-create_date')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_monitor_create_post(self):
        url = reverse('monitoring:monitor-list')
        data = {
            'name': 'test', 'asset': self.asset.id,
            'scrape_category': 'linux_system_memory', 'scrape_fields':json.dumps(['used']),
            'interval': 1, 'report_list': json.dumps(["diff"]), 'report_time':'0 8 * * *',
            'recipients': [self.super_user.id]
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check default value
        monitor = Monitor.objects.filter(name='test').first()
        self.assertEqual(monitor.scrape_parameters, {})
