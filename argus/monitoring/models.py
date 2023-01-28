from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class AccessType(models.TextChoices):
    ssh = 'ssh'


class Assets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(choices=AccessType.choices, max_length=15)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_asset_name_unique_constraints',
            )
        ]


class Secrets(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(choices=AccessType.choices, max_length=15)
    secret = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_secret_name_unique_constraints',
            )
        ]


class SSHAccessInfo(models.Model):
    asset = models.OneToOneField(Assets, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(
        65535)], default=22)  # possible ssh port range is 1 ~ 65535
    user_id = models.CharField(blank=True, null=True, max_length=31)
    password = models.CharField(blank=True, null=True, max_length=31)
    ssh_key = models.ForeignKey(Secrets, on_delete=models.SET_NULL, null=True)

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get("user_id")
        password = cleaned_data.get("password")
        ssh_key = cleaned_data.get("ssh_key")
        if not (user_id and password) or not ssh_key:
            raise ValidationError("ID/Password or SSHKey is required.")


class CustomCheckMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    target = models.CharField(max_length=31)  # process,cpu,memory,..

    class MethodType(models.TextChoices):
        cmdline = 'cmdline'
        file = 'file'
    method_type = models.CharField(choices=MethodType.choices, max_length=15)
    data = models.BinaryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_asset_name',
            )
        ]


class Monitoring(models.Model):
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE)

    class TargetSystem(models.TextChoices):
        linux = 'linux'
        # windows = 'windows'
        # kubernetes = 'kubernets'
    target_system = models.CharField(
        choices=TargetSystem.choices, max_length=15)
    scrap_info = models.JSONField(
        help_text="[{'type':'process','targets':['vsz','rss'],'interval':10,'get_pid_method':'custom_method'}}]")
    interval = models.IntegerField(validators=[MinValueValidator(
        1)], default=10, help_text="interval time as seconds.")
    reporting = models.BooleanField(default=False)
    report_receiver = models.JSONField(
        help_text="[{'type':'email', 'receivers':['test@email.com']}]")
