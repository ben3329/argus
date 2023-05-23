import sys
import subprocess
import asyncssh
import os
from pathlib import Path
import crypt
sys.path.append('..')

IP = '127.0.0.1'
PORT = 22
USERNAME = 'test'
PASSWORD = 'password'
PRIVATE_KEY = ''


def check_user_exists(username):
    result = subprocess.run(['id', username], capture_output=True, text=True)
    if result.returncode == 0:
        return True
    else:
        return False

def create_rsa(username):
    path = Path(f'/home/{username}/.ssh')
    path.mkdir(exist_ok=True)
    rsa_key = asyncssh.generate_private_key('ssh-rsa')
    pub = rsa_key.export_public_key()
    pkey = rsa_key.export_private_key()
    with open(f'/home/{username}/.ssh/authorized_keys', 'wb') as f:
        f.write(pub)
    with open(f'/home/{username}/.ssh/id_rsa.pub', 'wb') as f:
        f.write(pub)
    with open(f'/home/{username}/.ssh/id_rsa', 'wb') as f:
        f.write(pkey)

def prepare_ssh():
    global PRIVATE_KEY
    subprocess.run(['service', 'ssh', 'start'])
    if not check_user_exists(USERNAME):
        encrypted_password = crypt.crypt(PASSWORD)
        subprocess.run(['useradd', '-m', '-p', encrypted_password, USERNAME])
    if not os.path.exists(f'/home/{USERNAME}/.ssh/id_rsa'):
        create_rsa(USERNAME)
    with open(f'/home/{USERNAME}/.ssh/id_rsa', 'r') as f:
        PRIVATE_KEY = f.read()

prepare_ssh()