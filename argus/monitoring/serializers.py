from rest_framework import serializers
from .models import Asset, Secret, ScrapingCode, Monitor


class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['user', 'name', 'access_type', 'ip', 'port',
                  'user_id', 'username', 'password', 'ssh_key']


class SecretsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ['user', 'name', 'access_type', 'secret']


class ScrapingCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingCode
        fields = ['user', 'name', 'language',
                  'code', 'authority', 'output_type']


class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = ['asset', 'target_system', 'scrap_code', 'interval',
                  'reporting', 'report_time', 'report_receiver']
