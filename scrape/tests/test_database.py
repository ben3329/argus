from share import *
from database import *
from settings import *

import asyncio
import unittest
from tortoise.contrib.test import TestCase, initializer, finalizer


class TestDBClient(TestCase):
    def setUp(self):
        initializer(modules=['database'])

    def tearDown(self):
        finalizer()

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.dbclient = await DBClient(init_tortoise=False)
        self.scrape_name = 'test'

    async def test_insert_data(self):
        scrape = await self.dbclient.create_scrape(self.scrape_name)
        result = await self.dbclient.insert_data(scrape, {'key': 'value'})
        self.assertIsNotNone(result)
        scrapedata = await ScrapeData.all()
        self.assertIs(len(scrapedata), 1)

    async def test_insert_data_invalid(self):
        try:
            await self.dbclient.insert_data(self.scrape_name, {'key'})
        except InsertDataError:
            return
        self.assertFalse()

    async def test_delete_scrape(self):
        scrape = await self.dbclient.create_scrape(self.scrape_name)
        result = await self.dbclient.insert_data(scrape, {'key': 'value'})
        await self.dbclient.delete_scrape(scrape)
        scrapedata = await ScrapeData.all()
        self.assertIs(len(scrapedata), 0)


if __name__ == '__main__':
    asyncio.run(unittest.main())
