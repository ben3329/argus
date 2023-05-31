from share import *
from scrapemanger import *
from dataclass import *

import unittest
import asyncio
from tortoise.contrib.test import TestCase, initializer, finalizer


class TestScrapeManager(TestCase):
    def setUp(self):
        initializer(modules=['database'])
        with open('user_defined_script.py', 'r') as f:
            code = f.read()
        self.asset = {
            'ip': IP, 'port': PORT, 'asset_type': 'linux',
            'access_credential': {
                    'access_type': 'ssh_password',
                    'username': USERNAME,
                    'password': PASSWORD
                }}
        self.user_defined = {
            'name': 'test',
            'asset': self.asset,
            'scrape_category': 'user_defined_script',
            'scrape_fields': ['field1'],
            'scrape_parameters': {'--data': 2}, 
            'user_defined_script': {
                'name': 'test-script',
                'language': 'python3',
                'code': code,
                'output_type': 'json',
                'fields': ['field1', 'field2'],
                'parameters': ['--data'],
                'revision': 1
            },
            'interval': 5,
            'report_time': '* * * * *',
            'report_list': ['diff']}

        self.built_in = {
            'name': 'test',
            'asset': self.asset,
            'scrape_category': 'linux_system_memory',
            'scrape_fields': ['used'],
            'interval': 1,
            'report_time': '* * * * *',
            'report_list': ['diff']}

    def tearDown(self):
        finalizer()

    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_create_monitor_from_json_with_built_in_script(self):
        model = ScrapeModel.parse_obj(self.built_in)
        self.assertEqual(model.scrape_parameters, {})

    async def test_create_monitor_from_json_with_built_in_script_invalid_field(self):
        self.built_in['scrape_fields'] = ['invalid_field']
        try:
            model = ScrapeModel.parse_obj(self.built_in)
        except ValueError:
            pass
        except:
            self.assertFalse()

    async def test_create_monitor_from_json_with_user_defined_script(self):
        model = ScrapeModel.parse_obj(self.user_defined)

    async def test_create_monitor_from_json_with_user_defined_script_invalid_field(self):
        self.user_defined['scrape_fields'] = ['invalid_field']
        try:
            model = ScrapeModel.parse_obj(self.user_defined)
        except ValueError:
            pass
        except:
            self.assertFalse()

    async def test_create_monitor_from_json_with_user_defined_script_invalid_param(self):
        self.user_defined['scrape_parameters'] = {'--test':1}
        try:
            model = ScrapeModel.parse_obj(self.user_defined)
        except ValueError:
            pass
        except:
            self.assertFalse()

    async def test_scrape_built_in_linux_system_memory(self):
        model = ScrapeModel.parse_obj(self.built_in)
        scrape_manager = await ScrapeManager.create(model, init_tortoise=False)
        await scrape_manager.scrape_data()
        self.assertEqual(scrape_manager.status, 'Normal')
    
    async def test_scrape_built_in_linux_system_memory_with_pkey(self):
        self.asset['access_credential']['access_type'] = 'ssh_private_key'
        self.asset['access_credential']['secret'] = PRIVATE_KEY
        model = ScrapeModel.parse_obj(self.built_in)
        scrape_manager = await ScrapeManager.create(model, init_tortoise=False)
        await scrape_manager.scrape_data()
        self.assertEqual(scrape_manager.status, 'Normal')
    
    async def test_scrape_built_in_linux_system_memory_conn_error(self):
        self.asset['ip'] = '1.1.1.1'
        self.built_in['asset'] = self.asset
        model = ScrapeModel.parse_obj(self.built_in)
        scrape_manager = await ScrapeManager.create(model, init_tortoise=False)
        await scrape_manager.scrape_data()
        self.assertEqual(scrape_manager.status, 'TimeoutError')

    async def test_scrape_user_defined(self):
        model = ScrapeModel.parse_obj(self.user_defined)
        scrape_manager = await ScrapeManager.create(model, init_tortoise=False)
        await scrape_manager.scrape_data()
        self.assertEqual(scrape_manager.status, 'Normal')


if __name__ == '__main__':
    asyncio.run(unittest.main())
