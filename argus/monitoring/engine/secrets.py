from monitoring.models import *
from django.contrib.auth.models import User
import logging


class SecretsManager(object):
    def __init__(self, user: User) -> None:
        self.user = user

    def create_secret(self, name: str, access_type: AccessType, secret: str) -> bool:
        try:
            obj, created = Secret.objects.update_or_create(
                user=self.user, name=name, access_type=access_type, secret=secret)
        except Exception as e:
            logging.error(f'{self.user}: Fail to create secret. ' + str(e))
            return False
        return True

    def get_secret(self, name: str) -> Secret:
        return Secret.objects.filter(user=self.user, name=name).first()

    def delete_secret(self, name: str) -> bool:
        try:
            asset = Secret.objects.filter(user=self.user, name=name).first()
            asset.delete()
        except Exception as e:
            logging.error(f'{self.user}: Fail to delete secret. ' + str(e))
            return False
        return True
