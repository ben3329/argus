from django.test import TestCase
from django.contrib.auth import get_user_model

from monitoring.tasks import *
from monitoring.models import AccessCredential
from monitoring.choices import AccessTypeChoices
from monitoring.tests.common import CommonMethods

class TaskTest(TestCase, CommonMethods):
    def setUp(self):
        super().setUp()
        self.disconnect_signal()
        User = get_user_model()

        User.objects.create_superuser(
            username='admin', password='password', email='admin@myproject.com')
        self.super_user = User.objects.get(username='admin')
        self.ip='192.168.0.170'
        self.port = 22222
        self.access_cred = AccessCredential(
            name='test', username='root', password='sniper!#@$',
            access_type=AccessTypeChoices.ssh_password, author=self.super_user)
        self.access_cred.save()

    def test_access_test(self):
        result = access_test.delay(self.ip, self.port, self.access_cred.id)
        self.assertEqual(result.get(timeout=5)[0], True)

    def test_access_test_cannot_reach_ip(self):
        result = access_test.delay('1.1.1.1', self.port, self.access_cred.id)
        self.assertEqual(result.get(timeout=5)[0], False)
        
    def test_access_test_unknown_access_cred(self):
        result = access_test.delay(self.ip, self.port, self.access_cred.id+1)
        self.assertEqual(result.get(timeout=5)[0], False)