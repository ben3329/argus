from monitoring.models import *
from monitoring.serializers import *
from django.contrib.auth.models import User
import logging


class AssetsManager(object):
    def __init__(self, user: User) -> None:
        self.user = user

    def register_asset(self, name: str, access_type: AccessType) -> bool:
        try:
            query = Assets(user=self.user, name=name, access_type=access_type)
            query.save()
        except Exception as e:
            logging.warning(f"{self.user}: Fail to register asset: " + str(e))
            return False
        return True

    def get_assets_list(self) -> AssetsSerializer:
        assets = None
        if self.user.is_superuser:
            assets = Assets.objects.all()
        else:
            assets = Assets.objects.filter(user=self.user).all()
        return AssetsSerializer(assets, many=True)

    def delete_asset(self, user: User, name: str) -> bool:
        if not self.user.is_superuser and user != self.user:
            logging.warning(f"{self.user}: Cannot delete other user's asset")
            return False
        asset = Assets.objects.filter(user=user, name=name).first()
        asset.delete()
        return True
