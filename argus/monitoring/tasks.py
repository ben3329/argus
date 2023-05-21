from celery.utils.log import get_task_logger
from celery import shared_task
import os
import django
from monitoring.models import AccessCredential
from monitoring.choices import AccessTypeChoices
import paramiko
from typing import Tuple

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()


logger = get_task_logger(__name__)


def test_ssh_connection(hostname: str, port: int, username: str, password: str) -> Tuple[bool, str]:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, timeout=3,
                       username=username, password=password)
        return (True, 'OK')
    except Exception as e:
        return (False, str(e))
    finally:
        client.close()


@shared_task
def access_test(ip: str, port: int, access_credential_pk: int) -> Tuple[bool, str]:
    access_cred = AccessCredential.objects.filter(
        pk=access_credential_pk).all().first()
    result = None
    if access_cred:
        match access_cred.access_type:
            case AccessTypeChoices.ssh_password:
                result = test_ssh_connection(
                    hostname=ip, port=port,
                    username=access_cred.username, password=access_cred.password)
            case _:
                result = (False, 'Invalid Access Type')
    else:
        result = (False, 'There is no AccessCredential')
    return result
