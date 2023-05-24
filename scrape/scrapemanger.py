from report import *
from errors import *
from dataclass import *
from database import DBClient, Scrape
from logger import logger
import built_in_scripts

from typing import Dict, Union, Any, Literal
import asyncssh
import json
from collections import OrderedDict
from enum import Enum, auto
import traceback
import logging

class ScrapeMode(Enum):
    normal  = auto()
    debug = auto()

class ScrapeManager(object):
    def __init__(self, scrape_model: ScrapeModel, dbclient: DBClient, scrape: Scrape):
        self.scrape_model = scrape_model
        self._status: Literal['Normal', 'Error'] = 'Normal'
        self.dbclient = dbclient
        self.scrape = scrape
        self.mode = ScrapeMode.normal

    @classmethod
    async def create(cls, scrape_model: ScrapeModel, init_tortoise=True):
        dbclient = await DBClient(init_tortoise=init_tortoise)
        scrape = await dbclient.create_scrape(scrape_model.name)
        return cls(scrape_model, dbclient, scrape)

    @property
    def asset(self):
        return self.scrape_model.asset

    @property
    def access_credential(self):
        return self.scrape_model.asset.access_credential

    @property
    def status(self):
        return self._status

    def debug(self, func_name:str, msg:str):
        if self.mode == ScrapeMode.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"name: {self.scrape_model.name}, func:{func_name}, message:{msg}")

    async def set_status(self, value: str):
        if self._status != value:
            self._status = value
            await self.dbclient.set_scrape_status(self.scrape_model.name, value)

    async def scrape_data(self) -> None:
        self.debug('scrape_data', "Start Function")
        match self.scrape_model.scrape_category:
            case 'user_defined_script':
                try:
                    data = await self._user_defined_scrape()
                except Exception as e:
                    await self._error(e)
                    return
            case _:
                try:
                    data = await self._built_in_scrape()
                except Exception as e:
                    await self._error(e)
                    return
        self.debug('scrape_data', f"Data Exist. data: {data}")
        if data:
            try:
                if await self.dbclient.insert_data(self.scrape, data):
                    await self.set_status('Normal')
            except Exception as e:
                await self._error(e)
                return
        else:
            await self.set_status('Normal')
        self.debug('scrape_data', "Done Function")

    async def drop(self) -> None:
        try:
            self.dbclient.delete_scrape(name=self.scrape)
        except Exception as e:
            await self._error(e)

    async def report(self) -> None:
        self.debug('report', "Start Function")
        try:
            reporter = Reporter()
            df_first = await self.dbclient.get_first_data(self.scrape)
            df_24h = await self.dbclient.get_24h_data(self.scrape)
            scrape_data = ScrapeDTO(self.scrape_model.name, df_first, df_24h)
            await reporter.send_email(scrape_data, self.scrape_model.report_list, self.scrape_model.recipients)
        except Exception as e:
            await self._error(e)
        self.debug('report', "Done Function")

    async def _error(self, error: Exception) -> None:
        global logger
        logger.error(str(error))
        logger.error(traceback.format_exc())
        await self.set_status(type(error).__name__)

    async def _built_in_scrape(self) -> Dict[str, Union[int, float]]:
        self.debug('_built_in_scrape', "Start Function")
        self.debug('_built_in_scrape', f"Asset: {self.asset}")
        # connect to asset
        match self.access_credential.access_type:
            case 'ssh_password':
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              password=self.access_credential.password,
                                              known_hosts=None, connect_timeout=3)
            case 'ssh_private_key':
                pkey = asyncssh.import_private_key(self.access_credential.secret)
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              client_keys=[pkey],
                                              known_hosts=None, connect_timeout=3)
            case access_type:
                raise ValueError(
                    f"Invalid access_type. access_type:{access_type}")
        # set scraper and get data
        match (self.scrape_model.scrape_category , self.asset.asset_type):
            case 'linux_system_memory', 'linux':
                if self.scrape_model.scrape_parameters:
                    scraper = built_in_scripts.linux_system_memory.LinuxSystemMemory(
                        conn, **self.scrape_model.scrape_parameters)
                else:
                    scraper = built_in_scripts.linux_system_memory.LinuxSystemMemory(conn)
            case category, asset_type:
                raise ValueError(
                    f"Invalid built in script. category: {category}, asset_type: {asset_type}")
        await scraper.get_data()
        conn.close()
        result = OrderedDict()
        for field in self.scrape_model.scrape_fields:
            try:
                result.update({field: getattr(scraper, field)})
            except:
                result.update({field: None})
        self.debug('_built_in_scrape', "Done Function")
        return result

    async def _user_defined_scrape(self) -> Dict[str, Union[int, float]]:
        self.debug('_user_defined_scrape', "Start Function")
        result = None
        # connect to asset
        match self.access_credential.access_type:
            case 'ssh_password':
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              password=self.access_credential.password,
                                              known_hosts=None, connect_timeout=3)
            case 'ssh_private_key':
                pkey = asyncssh.import_private_key(self.access_credential.secret)
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              client_keys=[pkey],
                                              known_hosts=None, connect_timeout=3)
            case access_type:
                raise ValueError(
                    f"Invalid access_type. access_type:{access_type}")
        # upload script to asset
        script = self.scrape_model.user_defined_script
        match self.asset.asset_type:
            case 'linux':
                file_name = f'/tmp/{script.name}_{script.revision}'
                await self.__upload_script(conn, file_name)
            case asset_type:
                raise ValueError(
                    f"Invalid asset_type. access_type:{asset_type}")
        # run script
        param = ''
        if self.scrape_model.scrape_parameters:
            for key, value in self.scrape_model.scrape_parameters.items():
                param += f' {key} {value}'
        output = await conn.run(f"{script.language} {file_name} {param}", check=True)
        metric = output.stdout
        conn.close()
        if script.output_type == 'none':
            self.debug('_user_defined_scrape', "Done Function")
            return None
        else:
            self.debug('_user_defined_scrape', "Done Function")
            return self.__convert_metric_to_dict(
                metric, self.scrape_model.user_defined_script.output_type,
                self.scrape_model.scrape_fields)

    async def __upload_script(self, conn: asyncssh.SSHClientConnection, path: str):
        self.debug('__upload_script', "Start Function")
        async with conn.start_sftp_client() as sftp:
            try:
                async with sftp.open(path, 'w') as f:
                    await f.write(self.scrape_model.user_defined_script.code)
            except Exception as e:
                raise ScriptUploadError(
                    self.scrape_model.name, self.scrape_model.user_defined_script.name, str(e))
        self.debug('__upload_script', "Done Function")

    def __convert_metric_to_dict(self, metric: str, metric_type: str, fields: List[str]) -> Dict[str, Union[int, float]]:
        def is_valid_data(obj: Any) -> bool:
            if not isinstance(obj, dict):
                return False
            for key, value in obj.items():
                if not isinstance(key, str):
                    return False
                if not isinstance(value, (int, float)):
                    return False
            return True

        self.debug('__convert_metric_to_dict', "Start Function")
        if metric_type == 'json':
            data = json.loads(metric)
            if is_valid_data(data):
                selected_data = {k: data[k] for k in fields if k in data}
                result = selected_data
            else:
                raise ValueError(f"Invalid data type. Data:{data}")
        elif metric_type == 'csv':
            result = OrderedDict()
            data = metric.strip().split('\n')
            if len(data) != 2:
                raise ValueError(f"Invalid data type. Data:{data}")
            keys = data[0].strip().split(',')
            values = data[1].strip().split(',')
            if len(keys) != len(values):
                raise ValueError(f"Invalid data type. Data:{data}")
            for key, value in zip(keys, values):
                try:
                    value = int(value)
                except:
                    value = float(value)
                if key in fields:
                    result.update({key: value})
        self.debug('__convert_metric_to_dict', "Done Function")
        return result
