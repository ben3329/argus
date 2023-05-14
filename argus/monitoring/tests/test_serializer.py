from django.test import TestCase

from monitoring.models import *
from monitoring.serializers import MonitorToScrapeSerializer
from monitoring.tests.common import CommonMethods


class SerializerTests(TestCase, CommonMethods):
    def setUp(self):
        super().setUp()
        self.disconnect_signal()
        User.objects.create_superuser(
            username='admin', password='password', email='admin@myproject.com')
        self.super_user = User.objects.get(username='admin')
        self.cred = AccessCredential(
            author=self.super_user, name=f'{self.super_user.username}-id-password',
            access_type=AccessTypeChoices.ssh_password,
            username='root', password='sniper!#@$')
        self.cred.save()
        self.asset = Asset(
            author=self.super_user,
            ip='192.168.0.150', port=22, asset_type='linux',
            access_credential=self.cred)
        self.asset.save()
        self.user_defined_script = UserDefinedScript(
            author=self.super_user, name='test_script', language='bash',
            code='ls', output_type=OutputTypeChoices.none)
        self.user_defined_script.save()
        self.monitor = Monitor(
            name='test_monitor', asset=self.asset,
            scrape_category='linux_system_memory',
            scrape_fields=["used"],
            interval=1, report_list=["graph24", "diff"],
            report_time='0 8 * * *',
            author=self.super_user)
        self.monitor.save()
        self.monitor.recipients.add(self.super_user)

    def tearDown(self):
        self.connect_signal()
        super().tearDown()

    def test_monitor_to_scrape_serializer(self):
        serializer = MonitorToScrapeSerializer(self.monitor)
        data = serializer.data
        self.assertEqual(list(data), [
            'name', 'asset', 'scrape_category', 'scrape_fields', 'scrape_parameter',
            'user_defined_script', 'interval', 'report_time', 'report_list', 'recipients'])