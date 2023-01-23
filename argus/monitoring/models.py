from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.


class AccessType(models.TextChoices):
    ssh = 'ssh'

class Assets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(choices=AccessType.choices)

class Secrets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_type = models.CharField(choices=AccessType.choices)
    secret = models.TextField()

class SSHAccessInfo(models.Model):
    asset_id = models.ForeignKey(Assets, on_delete=models.CASCADE, db_column='asseets_id')
    ip = models.IPAddressField()
    port = models.IntegerField(min_value=1, max_value=65535, default=22) # possible ssh port range is 1 ~ 65535
    user_id = models.CharField(blank=True, null=True)
    password = models.CharField(blank=True, null=True)
    ssh_key_id = models.ForeignKey(Secrets, on_delete=models.SET_NULL, db_column='secrets_id')
    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get("user_id")
        password = cleaned_data.get("password")
        ssh_key_id = cleaned_data.get("ssh_key_id")
        if not (user_id and password) or not ssh_key_id:
            raise ValidationError("ID/Password or SSHKey is required.")

class Monitoring(models.Model):
    asset_id = models.ForeignKey(Assets, on_delete=models.CASCADE, db_column='asseets_id')
    class TargetSystem(models.TextChoices):
        linux = 'linux'
        # windows = 'windows'
        # kubernetes = 'kubernets'
    target_system = models.CharField(choices=TargetSystem.choices)
    scrap_info = models.JSONField(help_text="[{'type':'process','targets':['vsz','rss'],'interval':10}]")
    interval = models.IntegerField(min_value=1, default=10, help_text="interval time as seconds.")
    reporting = models.BooleanField(default=False)
    report_receiver = models.JSONField(help_text="[{'type':'email', 'receivers':['test@email.com']}]")