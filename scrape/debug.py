import redis
import json

redis_client = redis.Redis(host='redis', port=6379, db=0)
redis_client.lpush('web_to_engine', json.dumps({'cmd': 'list'}))
