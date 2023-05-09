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
            user=self.super_user, name=f'{self.super_user.username}-id-password',
            access_type=AccessTypeChoices.ssh_password,
            username='root', password='sniper!#@$')
        self.cred.save()
        self.asset = Asset(
            user=self.super_user,
            ip='192.168.0.150', port=22, asset_type='linux',
            access_credential=self.cred)
        self.asset.save()
        self.built_in_script = BuiltInScript(
            category='linux_system_memory', fields=["used"])
        self.built_in_script.save()
        self.user_defined_script = UserDefinedScript(
            author=self.super_user, name='test_script', language='bash',
            code='ls', authority=AuthorityChoices.public,
            output_type=OutputTypeChoices.none)
        self.user_defined_script.save()
        self.monitor = Monitor(
            name='test_monitor', asset=self.asset,
            built_in_script=self.built_in_script,
            interval=1, report_list=["graph24", "diff"],
            report_time='0 8 * * *',
            author=self.super_user)
        self.monitor.save()
        self.monitor.recipients.add(self.super_user)

    def tearDown(self):
        self.connect_signal()
        super().tearDown()

    def test_monitor_to_scrape_serializer_with_built_in(self):
        self.monitor.built_in_script = self.built_in_script
        self.monitor.user_defined_script = None
        serializer = MonitorToScrapeSerializer(self.monitor)
        data = serializer.data
        self.assertEqual(list(data), [
                         'name', 'asset', 'script', 'interval', 'report_list', 'report_time', 'recipients'])
        self.assertEqual(list(data['script']), [
                         'category', 'fields', 'parameter'])

    def test_monitor_to_scrape_serializer_with_user_defined(self):
        self.monitor.built_in_script = None
        self.monitor.user_defined_script = self.user_defined_script
        serializer = MonitorToScrapeSerializer(self.monitor)
        data = serializer.data
        self.assertEqual(list(data), [
                         'name', 'asset', 'script', 'interval', 'report_list', 'report_time', 'recipients'])
        self.assertEqual(list(data['script']), [
                         'name', 'language', 'code', 'output_type'])
