from share import *
from scrapemanger import *
from dataclass import *

import unittest
import asyncio
from tortoise.contrib.test import TestCase, initializer, finalizer


class TestScrapeManager(TestCase):
    def setUp(self):
        initializer(modules=['database'])
        access_credential = AccessCredentialModel(
            access_type='ssh_password', username=USERNAME, password=PASSWORD)
        asset = AssetModel(ip=IP, port=PORT, asset_type='linux',
                           access_credential=access_credential)
        script = UserDefinedScriptModel(name='test', language='bash',
                                        code='ls', output_type='none', revision=1)
        self.monitor = ScrapeModel(name='testm', asset=asset,
                                   script=script, interval=5, report_list=['diff'])

    def tearDown(self):
        finalizer()

    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_create_monitor_from_json_with_built_in_script(self):
        json_data = {
            'name': 'test',
            'asset': {
                'ip': '1.1.1.1',
                'port': 22,
                'asset_type': 'linux',
                'access_credential': {
                    'access_type': 'ssh_password',
                    'username': 'root',
                    'password': 'qwer1234'
                }},
            'script': {
                'category': 'linux_system_memory',
                'fields': ['used']
            },
            'interval': 5,
            'report_time': '* * * * *',
            'report_list': ['diff']}
        model = ScrapeModel.parse_obj(json_data)
        self.assertIsInstance(model.script, BuiltInScriptModel)

    async def test_create_monitor_from_json_with_user_defined_script(self):
        json_data = {
            'name': 'test',
            'asset': {
                'ip': '1.1.1.1',
                'port': 22,
                'asset_type': 'linux',
                'access_credential': {
                    'access_type': 'ssh_password',
                    'username': 'root',
                    'password': 'qwer1234'
                }},
            'script': {
                'name': 'test-script',
                'language': 'bash',
                'code': 'ls',
                'output_type': 'none',
                'revision': 1
            },
            'interval': 5,
            'report_time': '* * * * *',
            'report_list': ['diff']}
        model = ScrapeModel.parse_obj(json_data)
        self.assertIsInstance(model.script, UserDefinedScriptModel)

    async def test_scrape_built_in_linux_system_memory(self):
        script = BuiltInScriptModel(
            category='linux_system_memory', fields=['used'])
        self.monitor.script = script
        monitor_manager = await ScrapeManager.create(self.monitor, init_tortoise=False)
        await monitor_manager.scrape_data()
        self.assertEqual(monitor_manager.status, 'Normal')

    async def test_scrape_user_defined(self):
        monitor_manager = await ScrapeManager.create(self.monitor, init_tortoise=False)
        await monitor_manager.scrape_data()
        self.assertEqual(monitor_manager.status, 'Normal')


if __name__ == '__main__':
    asyncio.run(unittest.main())
