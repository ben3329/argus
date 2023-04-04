from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class AccessType(models.TextChoices):
    ssh_id_password = 'ssh_id_password', 'SSH ID Password'
    ssh_private_key = 'ssh_private_key', 'SSH Private Key'
    def __str__(self) -> str:
        return self.value[1]

class AssetType(models.TextChoices):
    linux = 'linux', 'Linux'
    windows = 'windows', 'Windows'


class AccessCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(choices=AccessType.choices, max_length=31, default='ssh_id_password')
    username = models.CharField(max_length=31, null=True, blank=True)
    password = models.CharField(max_length=31, null=True, blank=True)
    secret = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_access_credential_name_unique_constraints',
            )
        ]
    def __str__(self):
        return self.name


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(
        65535)], default=22)  # possible ssh port range is 1 ~ 65535
    asset_type = models.CharField(choices=AssetType.choices, max_length=15, default='linux')
    access_credential = models.ForeignKey(AccessCredential, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_asset_name_unique_constraints',
            )
        ]


class Script(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    create_date = models.DateTimeField(auto_now=True)

    class Language(models.TextChoices):
        python3 = 'python3'
        python2 = 'python2'
        bash = 'bash'
    language = models.CharField(choices=Language.choices, max_length=15)
    code = models.TextField()

    class Authority(models.TextChoices):
        public = 'public'
        private = 'private'
    authority = models.CharField(choices=Authority.choices, max_length=15)

    class OutputType(models.TextChoices):
        csv = 'csv'
        json = 'json'
        none = 'none'
    output_type = models.CharField(choices=OutputType.choices, max_length=15)


class Monitor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    create_date = models.DateTimeField(auto_now=True)

    class TargetSystem(models.TextChoices):
        linux = 'linux'
    target_system = models.CharField(
        choices=TargetSystem.choices, max_length=15)
    scrap_code = models.ForeignKey(
        Script, on_delete=models.SET_NULL, null=True, blank=True)
    interval = models.IntegerField(validators=[MinValueValidator(
        1)], default=10, help_text="interval time as seconds.")
    reporting = models.BooleanField(default=False)
    report_time = models.TimeField(null=True, blank=True)
    report_receiver = models.JSONField(null=True, blank=True, help_text="['user1', 'user2', ...]")
