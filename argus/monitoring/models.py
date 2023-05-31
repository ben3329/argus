from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from monitoring.choices import *


class AccessCredential(models.Model):
    name = models.CharField(max_length=31, unique=True)
    access_type = models.CharField(
        choices=AccessTypeChoices.choices, max_length=31)
    username = models.CharField(max_length=31)
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
        validators=[MinValueValidator(1), MaxValueValidator(65535)])
    asset_type = models.CharField(
        choices=AssetTypeChoices.choices, max_length=15)
    access_credential = models.ForeignKey(
        AccessCredential, on_delete=models.SET_NULL,
        null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)


class UserDefinedScript(models.Model):
    name = models.CharField(max_length=31, unique=True)
    language = models.CharField(
        choices=LanguageChoices.choices, max_length=15)
    code = models.TextField()
    output_type = models.CharField(
        choices=OutputTypeChoices.choices, max_length=15)
    fields = models.JSONField(null=True, blank=True)
    parameters = models.JSONField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    revision = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.revision += 1
        super().save(*args, **kwargs)


class Monitor(models.Model):
    name = models.CharField(max_length=31, unique=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    scrape_category = models.CharField(choices=ScrapeCategoryChoices.choices, max_length=31)
    scrape_fields = models.JSONField(blank=True, null=True)
    scrape_parameters = models.JSONField(blank=True, default=dict)
    user_defined_script = models.ForeignKey(
        UserDefinedScript, on_delete=models.SET_NULL, null=True, blank=True)
    interval = models.IntegerField(validators=[MinValueValidator(1)])
    report_time = models.CharField(max_length=15, null=True, blank=True)
    report_list = models.JSONField(null=True, blank=True)
    recipients = models.ManyToManyField(
        User, related_name='monitor_recipients', blank=True)
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
