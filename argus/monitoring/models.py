from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class AccessTypeChoices(models.TextChoices):
    ssh_id_password = 'ssh_id_password', 'SSH ID Password'
    ssh_private_key = 'ssh_private_key', 'SSH Private Key'

    def __str__(self) -> str:
        return self.value[1]


class AssetTypeChoices(models.TextChoices):
    linux = 'linux', 'Linux'
    windows = 'windows', 'Windows'


class AccessCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(
        choices=AccessTypeChoices.choices, max_length=31, default='ssh_id_password')
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
    asset_type = models.CharField(
        choices=AssetTypeChoices.choices, max_length=15, default='linux')
    access_credential = models.ForeignKey(
        AccessCredential, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_asset_name_unique_constraints',
            )
        ]


class LanguageChoices(models.TextChoices):
    python3 = 'python3'
    python2 = 'python2'
    shell = 'shell'


class AuthorityChoices(models.TextChoices):
    public = 'public'
    private = 'private'


class OutputTypeChoices(models.TextChoices):
    csv = 'csv'
    json = 'json'
    none = 'none'


class Script(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=31, help_text="The name of the script (max 31 characters).")
    language = models.CharField(
        choices=LanguageChoices.choices, max_length=15, help_text="The programming language of the script.")
    code = models.TextField(help_text="The code of the script.")
    authority = models.CharField(
        choices=AuthorityChoices.choices, max_length=15, help_text="The authority level of the script.")
    output_type = models.CharField(
        choices=OutputTypeChoices.choices, max_length=15, help_text="The output type of the script.")
    note = models.TextField(
        null=True, blank=True, help_text="Additional notes about the script (optional).")
    create_date = models.DateTimeField(
        auto_now=True, help_text="The date and time when the script was created.")
    update_date = models.DateTimeField(
        auto_now=True, help_text="The date and time when the script was last updated.")
    revision = models.IntegerField(
        default=1, help_text="The revision number of the script.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_script_name_unique_constraints',
            )
        ]


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
    report_receiver = models.JSONField(
        null=True, blank=True, help_text="['user1', 'user2', ...]")
