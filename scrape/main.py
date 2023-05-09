import redis.asyncio as redis
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
from scrapemanger import ScrapeManager 
from dataclass import *
from typing import Dict
from datetime import datetime
import pytz
from logger import logger
import logging
from settings import *
from database import Scrape


class Main(object):
    def __init__(self, redis_queue_name:str='web_to_engine', init_tortoise:bool=True) -> None:
        self.redis_server = redis.from_url(f'redis://{REDIS_HOST}')
        self.scrape_mgr_pool: Dict[str, ScrapeManager] = dict()
        self.scheduler = AsyncIOScheduler(logger=logger)
        self.scheduler.start()
        self.redis_queue_name = redis_queue_name
        self.init_tortoise = init_tortoise

    async def wait_running_job_complete(self):
        now = datetime.now(tz=pytz.UTC)
        while True:
            for job in self.scheduler.get_jobs():
                if job.next_run_time is not None and job.next_run_time <= now:
                    break
            else:
                break
            await asyncio.sleep(1)

    async def read_message(self) -> None:
        while True:
            _, message = await self.redis_server.brpop(self.redis_queue_name)
            try:
                message_data = json.loads(message.decode())
                if message_data['cmd'] == 'create':
                    scrape = ScrapeModel.parse_obj(
                        message_data['serialized_data'])
                    scrape_manager = await ScrapeManager.create(
                        scrape, init_tortoise=self.init_tortoise)
                    scrape_job_id = scrape.name + '_scrape'
                    report_job_id = scrape.name + '_report'
                    await self.wait_running_job_complete()
                    self.scheduler.pause()
                    # create scrape job
                    if self.scheduler.get_job(scrape_job_id):
                        self.scheduler.remove_job(scrape_job_id)
                    self.scheduler.add_job(
                        scrape_manager.scrape_data, 'interval', seconds=scrape.interval,
                        id=scrape_job_id)
                    # create report job
                    if self.scheduler.get_job(report_job_id):
                        self.scheduler.remove_job(report_job_id)
                    if scrape.report_time:
                        self.scheduler.add_job(
                            scrape_manager.report, 'cron', **scrape.report_time_as_dict,
                            id=report_job_id)
                    self.scheduler.resume()
                    self.scrape_mgr_pool[scrape.name] = scrape_manager
                elif message_data['cmd'] == 'stop':
                    await self.stop_scrape(message_data['name'])
                elif message_data['cmd'] == 'delete':
                    await self.stop_scrape(message_data['name'])
                    await Scrape.all().delete()
                elif message_data['cmd'] == 'list':
                    jobs = self.scheduler.get_jobs()
                    jobs_str = f'jobs: {jobs}'
                    logger.setLevel(logging.INFO)
                    logger.info(jobs_str)
                    logger.setLevel(logging.WARNING)
                    print(jobs_str)
                else:
                    raise ValueError(
                        f"Unknown command. cmd: {message_data['cmd']}")
            except Exception as e:
                logger.warning(
                    f"{type(e).__name__}. message: {message}, error_message: {e}")

    async def stop_scrape(self, scrape_name:str):
        scrape_job_id = scrape_name + '_scrape'
        report_job_id = scrape_name + '_report'
        await self.wait_running_job_complete()
        self.scheduler.pause()
        if self.scheduler.get_job(scrape_job_id):
            self.scheduler.remove_job(scrape_job_id)
        if self.scheduler.get_job(report_job_id):
            self.scheduler.remove_job(report_job_id)
        self.scheduler.resume()
        if scrape_name in self.scrape_mgr_pool:
            del self.scrape_mgr_pool[scrape_name]

    def run(self):
        print('start scrape')
        asyncio.run(self.read_message())

if __name__ == '__main__':
    program = Main()
    program.run()