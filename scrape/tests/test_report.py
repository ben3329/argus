from share import *
import unittest
from database import *
from report import *
from dataclass import *
import asyncio
from datetime import datetime, timedelta

from tortoise.contrib.test import TestCase, initializer, finalizer


class TestReporter(TestCase):
    def setUp(self):
        initializer(modules=['database'])

    def tearDown(self):
        finalizer()

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.dbclient = await DBClient(init_tortoise=False)
        self.scrape_name = 'test'
        scrape = await self.dbclient.create_scrape(self.scrape_name)
        for i in range(30):
            data = {'col1': 1 + i, 'col2': 2 - i}
            datetime_field = datetime.utcnow() - timedelta(hours=32-i)
            await self.dbclient.insert_data(
                scrape, data, datetime=datetime_field)

        df_first = await self.dbclient.get_first_data(scrape)
        df_24h = await self.dbclient.get_24h_data(scrape)

        self.data = ScrapeDTO(self.scrape_name, df_first, df_24h)
        self.reporter = Reporter()

    async def test_create_stats_massage(self):
        result = self.reporter.create_stats_message(
            self.data, ['avg24', 'var24', 'std24'])
        self.assertIsInstance(result, str)
        self.assertIn('Average', result)
        self.assertIn('Variance', result)
        self.assertIn('Standard Deviation', result)

    async def test_create_image_message(self):
        result = self.reporter.create_image_message(self.data, 'graph24')
        self.assertIsInstance(result, str)
        self.assertIn('<img src="data:image/png;base64', result)

    async def test_create_change_massage(self):
        result = self.reporter.create_change_message(self.data, 'diff')
        self.assertIsInstance(result, str)
        self.assertIn('diff', result)
    # If you want to test send email remove comments.
    # async def test_send_email(self):
    #     await self.reporter.send_email(
    #         self.data,
    #         ['graph24', 'avg24', 'var24', 'std24', 'diff', 'diff24'],
    #         recipients=['ben3329@naver.com'], css='../email.css')


if __name__ == '__main__':
    asyncio.run(unittest.main())
