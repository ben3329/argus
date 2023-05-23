from django.db.models.signals import post_save, pre_delete
from monitoring.models import * 
from monitoring.signals import create_scrape, stop_scrape
import subprocess
import paramiko
import os
from pathlib import Path
import crypt


class CommonMethods(object):
    ip = '127.0.0.1'
    port = 22
    username = 'test'
    password = 'password'
    pkey = ''
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
    
    def prepare_ssh(self):
        subprocess.run(['service', 'ssh', 'start'])
        if not self._check_user_exists(self.username):
            encrypted_password = crypt.crypt(self.password)
            subprocess.run(['useradd', '-m', '-p', encrypted_password, self.username])
        if not os.path.exists(f'/home/{self.username}/.ssh/id_rsa'):
            self._create_rsa(self.username)
        with open(f'/home/{self.username}/.ssh/id_rsa', 'r') as f:
            self.pkey = f.read()

    def _check_user_exists(self, username):
        result = subprocess.run(['id', username], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            return False

    def _create_rsa(self, username):
        path = Path(f'/home/{username}/.ssh')
        path.mkdir(exist_ok=True)
        rsa_key = paramiko.RSAKey.generate(2048)
        with open(f'/home/{username}/.ssh/authorized_keys', 'w') as f:
            f.write(rsa_key.get_base64())
        rsa_key.write_private_key_file(f'/home/{username}/.ssh/id_rsa')

