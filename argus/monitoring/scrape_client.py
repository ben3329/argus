from monitoring.serializers import MonitorToScrapeSerializer
from monitoring.models import Monitor 

import redis
import json
from typing import List


class ScrapeClient:
    _instance = None
    _redis_client = None
    _redis_queue_name = 'web_to_engine'

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._redis_client = redis.Redis(host='redis', port=6379, db=0)
        return cls._instance

    def create(self, instance_list: List[Monitor]):
        for instance in instance_list:
            serialized_data = MonitorToScrapeSerializer(instance=instance).data
            self._redis_client.lpush(
                self._redis_queue_name,
                json.dumps({'cmd': 'create', 'serialized_data': serialized_data}))

    def delete(self, monitor_name: str):
        cmd = {'cmd': 'delete', 'name': monitor_name}
        self._redis_client.lpush(
            self._redis_queue_name,
            json.dumps(cmd))

    def stop(self, monitor_name: str):
        cmd = {'cmd': 'stop', 'name': monitor_name}
        self._redis_client.lpush(
            self._redis_queue_name,
            json.dumps(cmd))
