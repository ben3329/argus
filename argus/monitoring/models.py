from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class AccessType(models.TextChoices):
    ssh = 'ssh'


class Secret(models.Model):
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


class Asset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)
    access_type = models.CharField(choices=AccessType.choices, max_length=15)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(
        65535)], default=22)  # possible ssh port range is 1 ~ 65535
    username = models.CharField(blank=True, null=True, max_length=31)
    password = models.CharField(blank=True, null=True, max_length=31)
    ssh_key = models.ForeignKey(Secret, on_delete=models.SET_NULL, null=True, blank=True)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     user_id = cleaned_data.get("user_id")
    #     password = cleaned_data.get("password")
    #     ssh_key = cleaned_data.get("ssh_key")
    #     if not (user_id and password) or not ssh_key:
    #         raise ValidationError("ID/Password or SSHKey is required.")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='user_asset_name_unique_constraints',
            )
        ]


class ScrapingCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=31)

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

    class TargetSystem(models.TextChoices):
        linux = 'linux'
    target_system = models.CharField(
        choices=TargetSystem.choices, max_length=15)
    scrap_code = models.ForeignKey(
        ScrapingCode, on_delete=models.SET_NULL, null=True, blank=True)
    interval = models.IntegerField(validators=[MinValueValidator(
        1)], default=10, help_text="interval time as seconds.")
    reporting = models.BooleanField(default=False)
    report_time = models.TimeField(null=True, blank=True)
    report_receiver = models.JSONField(null=True, blank=True, help_text="['user1', 'user2', ...]")
