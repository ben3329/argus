from rest_framework import serializers
from .models import Assets, Secrets, ScrapingCodes, Monitoring


class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = ['user', 'name', 'access_type', 'ip', 'port',
                  'user_id', 'username', 'password', 'ssh_key']


class SecretsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secrets
        fields = ['user', 'name', 'access_type', 'secret']


class ScrapingCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingCodes
        fields = ['user', 'name', 'language',
                  'code', 'authority', 'output_type']


class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitoring
        fields = ['asset', 'target_system', 'scrap_code', 'interval',
                  'reporting', 'report_time', 'report_receiver']
