from settings import *
from errors import *

from datetime import datetime, timedelta
import pytz
import pandas as pd
from collections import OrderedDict
from tortoise import Tortoise, fields
from tortoise.models import Model
from typing import Union, Dict


class Scrape(Model):
    name = fields.CharField(max_length=31, pk=True)
    status = fields.CharField(max_length=31, default='Normal')

    class Meta:
        db_table = 'scrape'


class ScrapeData(Model):
    scrape = fields.ForeignKeyField(
        'models.Scrape', on_delete=fields.CASCADE, reference='Scrape')
    datetime = fields.DatetimeField(auto_now_add=True)
    data = fields.JSONField()

    class Meta:
        table = 'scrape_data'


class DBClient:
    _instance = None

    async def __new__(cls, init_tortoise=True):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            if init_tortoise:
                await Tortoise.init(
                    db_url=f'mysql://root:{DB_PASSWORD}@{DB_HOST}/monitoring',
                    modules={'models': ['database']}
                )
                await Tortoise.generate_schemas()
        return cls._instance

    async def create_scrape(self, name: str) -> Scrape:
        await Scrape.filter(name=name, status='Deleted').delete()
        scrape, created = await Scrape.get_or_create(name=name)
        if created == False:
            scrape.status = 'Normal'
            await scrape.save()
        return scrape

    async def set_scrape_status(self, name: str, status: str):
        await Scrape.filter(name=name).update(status=status)

    async def insert_data(self, scrape: Scrape, data: Dict[str, Union[int, float]], datetime=None) -> ScrapeData:
        result = None
        try:
            if datetime:
                result = await ScrapeData.create(scrape=scrape, data=data, datetime=datetime)
            else:
                result = await ScrapeData.create(scrape=scrape, data=data)
        except Exception as e:
            raise InsertDataError(scrape, data, str(e))
        return result

    async def delete_scrape(self, scrape: Scrape):
        await scrape.delete()

    async def get_24h_data(self, scrape: Scrape) -> pd.DataFrame:
        now = datetime.utcnow()
        past_24h = now - timedelta(hours=24)
        data_list = await ScrapeData.filter(scrape=scrape).filter(datetime__gte=past_24h, datetime__lte=now).all()
        rows = []
        for data in data_list:
            row = OrderedDict(
                [('datetime', data.datetime.astimezone(pytz.timezone(TZ)))])
            row.update(data.data)
            rows.append(row)
        return pd.DataFrame(rows)

    async def get_first_data(self, scrape: Scrape) -> pd.DataFrame:
        data = await ScrapeData.filter(scrape=scrape).all().order_by('datetime').first()
        row = OrderedDict(
            [('datetime', data.datetime.astimezone(pytz.timezone(TZ)))])
        row.update(data.data)
        return pd.DataFrame([row])
