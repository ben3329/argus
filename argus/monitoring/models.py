from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class AccessTypeChoices(models.TextChoices):
    ssh_password = 'ssh_password', 'SSH Password'
    ssh_private_key = 'ssh_private_key', 'SSH Private Key'

    def __str__(self) -> str:
        return self.value[1]


class AssetTypeChoices(models.TextChoices):
    linux = 'linux', 'Linux'


class AccessCredential(models.Model):
    name = models.CharField(max_length=31, unique=True)
    access_type = models.CharField(
        choices=AccessTypeChoices.choices, max_length=31)
    username = models.CharField(max_length=31, null=True, blank=True)
    password = models.CharField(max_length=31, null=True, blank=True)
    secret = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    name = models.CharField(max_length=31, unique=True)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        default=22)
    asset_type = models.CharField(
        choices=AssetTypeChoices.choices, max_length=15)
    access_credential = models.ForeignKey(
        AccessCredential, on_delete=models.SET_NULL,
        null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)


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


class UserDefinedScript(models.Model):
    name = models.CharField(max_length=31)
    language = models.CharField(
        choices=LanguageChoices.choices, max_length=15)
    code = models.TextField()
    output_type = models.CharField(
        choices=OutputTypeChoices.choices, max_length=15)
    note = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    revision = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.revision += 1
        super().save(*args, **kwargs)


class CategoryChoices(models.TextChoices):
    linux_system_memory = 'linux_system_memory'


class BuiltInScript(models.Model):
    category = models.CharField(
        choices=CategoryChoices.choices, max_length=31)
    fields = models.JSONField()
    parameter = models.JSONField(blank=True, null=True)


class Monitor(models.Model):
    name = models.CharField(max_length=31, unique=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    built_in_script = models.ForeignKey(
        BuiltInScript, on_delete=models.SET_NULL, null=True, blank=True)
    user_defined_script = models.ForeignKey(
        UserDefinedScript, on_delete=models.SET_NULL, null=True, blank=True)
    interval = models.IntegerField(validators=[MinValueValidator(1)])
    report_time = models.CharField(max_length=15, null=True, blank=True)
    report_list = models.JSONField()
    recipients = models.ManyToManyField(
        User, related_name='monitor_recipients')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='monitors')
    create_date = models.DateTimeField(auto_now_add=True)


class Scrape(models.Model):
    name = models.CharField(max_length=31, primary_key=True)
    status = models.CharField(max_length=31, default='Normal')

    class Meta:
        db_table = 'scrape'


class ScrapeData(models.Model):
    scrape = models.ForeignKey(Scrape, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    class Meta:
        db_table = 'scrape_data'
