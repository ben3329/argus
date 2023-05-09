from share import *
from settings import *
from database import *
from main import Main
from logger import log_path

import asyncio
import unittest
from tortoise.contrib.test import TestCase, initializer, finalizer
import redis.asyncio as redis
import json


class TestMain(TestCase):
    def setUp(self):
        initializer(modules=['database'])
        self.redis_queue_name = 'test'
        self.main = Main(redis_queue_name=self.redis_queue_name,
                         init_tortoise=False)
        loop = asyncio.get_event_loop()
        loop.create_task(self.main.read_message())
        self.redis = redis.from_url(f'redis://{REDIS_HOST}')
        self.scrape_name = 'test'
        self.create_data = {
            'name': self.scrape_name,
            'asset': {
                'ip': IP,
                'port': PORT,
                'asset_type': 'linux',
                'access_credential': {
                    'access_type': 'ssh_password',
                    'username': USERNAME,
                    'password': PASSWORD
                }},
            'script': {
                'category': 'linux_system_memory',
                'fields': ['used']
            },
            'interval': 1,
            'report_time': '* * * * *',
            'report_list': ['diff']}
        self.create_cmd = {'cmd': 'create',
                           'serialized_data': self.create_data}
        with open(log_path, 'w') as f:
            pass

    def tearDown(self):
        finalizer()

    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def asyncTearDown(self):
        await self.redis.lpush(self.redis_queue_name, json.dumps({'cmd:': 'exit'}))
        await self.redis.close()
        await asyncio.sleep(2)
        await super().asyncTearDown()

    async def test_cmd_create(self):
        await self.redis.lpush(self.redis_queue_name, json.dumps(self.create_cmd))
        await asyncio.sleep(2)
        self.assertEqual(len(self.main.scheduler.get_jobs()), 2)
        scrape = await Scrape.all()
        self.assertEqual(len(scrape), 1)
        scrape_data = await ScrapeData.all()
        self.assertNotEqual(len(scrape_data), 0)
        self.assertEqual(list(self.main.scrape_mgr_pool), [self.scrape_name])

    async def test_cmd_list(self):
        list_cmd = {'cmd': 'list'}
        await self.redis.lpush(self.redis_queue_name, json.dumps(self.create_cmd))
        await self.redis.lpush(self.redis_queue_name, json.dumps(list_cmd))
        await asyncio.sleep(2)
        with open(log_path, 'r') as f:
            log = f.read()
        self.assertIn('INFO jobs:', log)

    async def test_cmd_stop(self):
        stop_cmd = {'cmd': 'stop', 'name': self.scrape_name}
        await self.redis.lpush(self.redis_queue_name, json.dumps(self.create_cmd))
        await asyncio.sleep(2)
        await self.redis.lpush(self.redis_queue_name, json.dumps(stop_cmd))
        await asyncio.sleep(1)
        self.assertEqual(len(self.main.scheduler.get_jobs()), 0)
        scrape = await Scrape.all()
        self.assertEqual(len(scrape), 1)
        scrape_data = await ScrapeData.all()
        self.assertNotEqual(len(scrape_data), 0)
        self.assertEqual(list(self.main.scrape_mgr_pool), [])

    async def test_cmd_delete(self):
        delete_cmd = {'cmd': 'delete', 'name': self.scrape_name}
        await self.redis.lpush(self.redis_queue_name, json.dumps(self.create_cmd))
        await asyncio.sleep(2)
        await self.redis.lpush(self.redis_queue_name, json.dumps(delete_cmd))
        await asyncio.sleep(1)
        self.assertEqual(len(self.main.scheduler.get_jobs()), 0)
        scrape = await Scrape.all()
        self.assertEqual(len(scrape), 0)
        scrape_data = await ScrapeData.all()
        self.assertEqual(len(scrape_data), 0)
        self.assertEqual(list(self.main.scrape_mgr_pool), [])


if __name__ == '__main__':
    asyncio.run(unittest.main())
