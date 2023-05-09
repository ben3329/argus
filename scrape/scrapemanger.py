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


class ScrapeManager(object):
    def __init__(self, scrape_model: ScrapeModel, dbclient: DBClient, scrape: Scrape):
        self.scrape_model = scrape_model
        self._status: Literal['Normal', 'Error'] = 'Normal'
        self.dbclient = dbclient
        self.scrape = scrape

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
    def script(self):
        return self.scrape_model.script

    @property
    def status(self):
        return self._status

    async def set_status(self, value: str):
        if self._status != value:
            self._status = value
            await self.dbclient.set_scrape_status(self.scrape_model.name, value)

    async def scrape_data(self) -> None:
        match self.script:
            case BuiltInScriptModel():
                try:
                    data = await self._built_in_scrape()
                except Exception as e:
                    await self._error(e)
                    return
            case UserDefinedScriptModel():
                try:
                    data = await self._user_defined_scrape()
                except Exception as e:
                    await self._error(e)
                    return
            case _:
                raise
        if data:
            try:
                if await self.dbclient.insert_data(self.scrape, data):
                    await self.set_status('Normal')
            except Exception as e:
                await self._error(e)
                return
        else:
            await self.set_status('Normal')

    async def drop(self) -> None:
        try:
            self.dbclient.delete_scrape(name=self.scrape)
        except Exception as e:
            await self._error(e)

    async def report(self) -> None:
        try:
            reporter = Reporter()
            df_first = await self.dbclient.get_first_data(self.scrape)
            df_24h = await self.dbclient.get_24h_data(self.scrape)
            scrape_data = ScrapeDTO(self.scrape_model.name, df_first, df_24h)
            await reporter.send_email(scrape_data, self.scrape_model.report_list, self.scrape_model.recipients)
        except Exception as e:
            await self._error(e)

    async def _error(self, error: Exception) -> None:
        global logger
        logger.warning(str(error))
        await self.set_status(type(error).__name__)

    async def _built_in_scrape(self) -> Dict[str, Union[int, float]]:
        # connect to asset
        match self.access_credential.access_type:
            case 'ssh_password':
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              password=self.access_credential.password,
                                              known_hosts=None)
            case access_type:
                raise ValueError(
                    f"Invalid access_type. access_type:{access_type}")
        # set scraper and get data
        match (self.script.category, self.asset.asset_type):
            case 'linux_system_memory', 'linux':
                scraper = built_in_scripts.linux_system_memory.LinuxSystemMemory(
                    conn)
            case category, asset_type:
                raise ValueError(
                    f"Invalid built in script. category: {category}, asset_type: {asset_type}")
        await scraper.get_data()
        conn.close()
        result = OrderedDict()
        for field in self.script.fields:
            try:
                result.update({field: getattr(scraper)})
            except:
                result.update({field: None})
        return result

    async def _user_defined_scrape(self) -> Dict[str, Union[int, float]]:
        result = None
        # connect to asset
        match self.access_credential.access_type:
            case 'ssh_password':
                conn = await asyncssh.connect(host=self.asset.ip, port=self.asset.port,
                                              username=self.access_credential.username,
                                              password=self.access_credential.password,
                                              known_hosts=None)
            case access_type:
                raise ValueError(
                    f"Invalid access_type. access_type:{access_type}")
        # upload script to asset
        match self.asset.asset_type:
            case 'linux':
                file_name = f'/tmp/{self.script.name}_{self.script.revision}'
                await self.__upload_script(conn, file_name)
            case asset_type:
                raise ValueError(
                    f"Invalid asset_type. access_type:{asset_type}")
        # run script
        output = await conn.run(f"{self.script.language} {file_name}")
        conn.close()
        if self.script.output_type == 'none':
            return None
        else:
            return self.__convert_metric_to_dict(output.stdout)

    async def __upload_script(self, conn: asyncssh.SSHClientConnection, path: str):
        async with conn.start_sftp_client() as sftp:
            try:
                async with sftp.open(path, 'w') as f:
                    await f.write(self.script.code)
            except Exception as e:
                raise ScriptUploadError(
                    self.scrape_model.name, self.script.name, str(e))

    def __convert_metric_to_dict(self, metric: str) -> Dict[str, Union[int, float]]:
        def is_valid_data(obj: Any) -> bool:
            if not isinstance(obj, dict):
                return False
            for key, value in obj.items():
                if not isinstance(key, str):
                    return False
                if not isinstance(value, (int, float)):
                    return False
            return True

        if self.script.output_type == 'json':
            data = json.loads(metric)
            if is_valid_data(data):
                result = data
            else:
                raise ValueError(f"Invalid data type. Data:{data}")
        elif self.script.output_type == 'csv':
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
                result.update({key: value})
        return result
