from monitoring.models import *
import logging
from io import StringIO
import paramiko


class SSHAccessInfoManager(object):
    def __init__(self, asset: Asset) -> None:
        self.asset = asset

    def create_access_info_with_account(self, ip: str, port: int, user_id: str, password: str) -> bool:
        try:
            obj, created = SSHAccessInfo.objects.update_or_create(
                asset=self.asset, ip=ip, port=port, user_id=user_id, password=password)
        except Exception as e:
            logging.error('Fail to create ssh info. ' + str(e))
            return False
        return True

    def create_access_info_with_pkey(self, ip: str, port: int, ssh_key: Secret) -> bool:
        try:
            obj, created = SSHAccessInfo.objects.update_or_create(
                asset=self.asset, ip=ip, port=port, ssh_key=ssh_key)
        except Exception as e:
            logging.error('Fail to create ssh info. ' + str(e))
            return False
        return True


class SSHObject(object):
    def __init__(self, access_info_id: int) -> None:
        self.ssh_info = SSHAccessInfo.objects.filter(id=access_info_id).first()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def open_ssh_connection(self) -> bool:
        channel = self.ssh.invoke_shell()
        if channel == None:
            try:
                if self.ssh_info.ssh_key:
                    secret = Secret.objects.values(
                        'secret').get(id=self.ssh_info.ssh_key)
                    private_key = paramiko.rsakey.RSAKey.from_private_key(
                        StringIO(secret))
                    self.ssh.connect(hostname=self.ssh_info.ip,
                                     port=self.ssh_info.port, pkey=private_key)
                else:
                    self.ssh.connect(
                        hostname=self.ssh_info.ip, port=self.ssh_info.port,
                        username=self.ssh_info.user_id, password=self.ssh_info.password)
            except Exception as e:
                logging.warning("Fail to connect ssh: " + str(e))
                return False
        return True
