from share import *
import unittest

from database import *
import asyncio
from settings import *

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


# from tortoise import Tortoise, generate_config
# class TestDBClient(unittest.IsolatedAsyncioTestCase):
#     async def asyncSetUp(self):
#         config = generate_config('sqlite://:memory:', app_modules={'models': ['database']},
#                                  testing=True, connection_label='models')
#         await Tortoise.init(config, _create_db=True)
#         await Tortoise.generate_schemas(safe=False)
#         self.dbclient = await DBClient(init_tortoise=False)
#         self.scrape_name = 'test'
#         print(config)

#     async def asyncTearDown(self):
#         await Tortoise._drop_databases()


if __name__ == '__main__':
    asyncio.run(unittest.main())
