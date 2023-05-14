from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from monitoring.models import *
from monitoring.scrape_client import ScrapeClient

@receiver(post_save, sender=Monitor)
@receiver(post_save, sender=Asset)
@receiver(post_save, sender=AccessCredential)
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
        case UserDefinedScript():
            instance_list = Monitor.objects.filter(user_defined_script=instance)
    
    scrape_client = ScrapeClient()
    scrape_client.create(instance_list=instance_list)
