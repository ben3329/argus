from django.test import TestCase
from django.db.models.signals import post_save, pre_delete
from monitoring.models import * 
from monitoring.signals import create_scrape, stop_scrape

class CommonMethods(object):
    def connect_signal(self):
        post_save.connect(create_scrape, sender=Monitor)
        post_save.connect(create_scrape, sender=Asset)
        post_save.connect(create_scrape, sender=AccessCredential)
        post_save.connect(create_scrape, sender=UserDefinedScript)
        pre_delete.connect(stop_scrape, sender=Monitor)

    def disconnect_signal(self):
        post_save.disconnect(create_scrape, sender=Monitor)
        post_save.disconnect(create_scrape, sender=Asset)
        post_save.disconnect(create_scrape, sender=AccessCredential)
        post_save.disconnect(create_scrape, sender=UserDefinedScript)
        pre_delete.disconnect(stop_scrape, sender=Monitor)