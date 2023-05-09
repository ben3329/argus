from django.db.models.signals import post_save
from django.dispatch import receiver
from monitoring.models import *
from monitoring.serializers import MonitorSerializer
import json
import redis

@receiver(post_save, sender=Monitor)
@receiver(post_save, sender=Asset)
@receiver(post_save, sender=AccessCredential)
@receiver(post_save, sender=BuiltInScript)
@receiver(post_save, sender=UserDefinedScript)
def create_scrape(sender, instance, **kwargs):
    instance_list = []
    match instance:
        case Monitor():
            instance_list.append(instance)
        case Asset():
            instance_list = Monitor.objects.filter(asset=instance)
        case AccessCredential():
            instance_list = Monitor.objects.filter(asset__access_credential=instance)
        case BuiltInScript():
            instance_list = Monitor.objects.filter(built_in_script=instance)
        case UserDefinedScript():
            instance_list = Monitor.objects.filter(user_defined_script=instance)
    
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    for instance in instance_list:
        serialized_data = MonitorSerializer(instance=instance).data
        redis_client.lpush(
            'web_to_engine',
            json.dumps({'cmd':'create', 'serialized_data':serialized_data}))
