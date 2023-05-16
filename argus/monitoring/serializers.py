from rest_framework import serializers
from monitoring.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AccessCredentialSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['id', 'name', 'access_type']

class AssetSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name']

class UserDefinedScriptSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = UserDefinedScript
        fields = ['id', 'name', 'fields', 'parameters']


class AssetViewSetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_detail = UserSerializer(source='author', read_only=True)
    access_credential = serializers.PrimaryKeyRelatedField(
        queryset=AccessCredential.objects.all())
    access_credential_detail = AccessCredentialSerializerSimple(
        source='access_credential', read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'name', 'ip', 'port', 'asset_type',
                  'access_credential', 'access_credential_detail', 'note',
                  'author', 'author_detail', 'create_date']
        read_only_fields = ['author_detail', 'access_credential_detail', 'create_date'] 


class AccessCredentialViewSetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = AccessCredential
        fields = ['id', 'name', 'access_type',
                  'username', 'password', 'secret', 'note', 
                  'author', 'author_detail', 'create_date']
        read_only_fields = ['author_detail', 'create_date'] 

    def validate_access_type(self, value):
        if ('_password') in value:
            if self.initial_data.get('password') == None:
                raise serializers.ValidationError(
                    "username and password field is required.")
        else:
            if self.initial_data.get('secret') == None:
                raise serializers.ValidationError(
                    "secret field is required.")
        return value

    def validate_password(self, value):
        if ('_password' in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_secret(self, value):
        if ('_password' not in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")
        return value


class UserDefinedScriptViewSetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = UserDefinedScript
        fields = ['id', 'name', 'language', 'code',
                  'output_type', 'fields', 'parameters',
                  'note', 'author', 'author_detail',
                  'create_date', 'update_date', 'revision']
        read_only_fields = ['author_detail', 'create_date', 'update_date', 'revision'] 


class MonitorViewSetSerializer(serializers.ModelSerializer):
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())
    asset_name = serializers.ReadOnlyField(source='asset.name')
    user_defined_script = serializers.PrimaryKeyRelatedField(
        queryset=UserDefinedScript.objects.all(),
        allow_null=True, required=False)
    user_defined_script_name = serializers.ReadOnlyField(source='user_defined_script.name')
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_name = serializers.ReadOnlyField(source='author.username')
    scrape_status = serializers.SerializerMethodField()

    class Meta:
        model = Monitor
        fields = ['id', 'name', 'asset', 'asset_name',
                  'scrape_category', 'scrape_fields', 'scrape_parameters',
                  'user_defined_script', 'user_defined_script_name',
                  'scrape_status',
                  'interval', 'report_time', 'report_list', 'recipients',
                  'author', 'author_name', 'create_date']
        read_only_fields = ['asset_name', 'user_defined_script_name',
                            'scrape_status', 'author_name', 'create_date']
    def get_scrape_status(self, obj):
        scrape = Scrape.objects.filter(name=obj.name).first()
        return scrape.status if scrape else None


# For scrape client
class AccessCredentialToScrapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['access_type', 'username', 'password', 'secret']


class AssetToScrapeSerializer(serializers.ModelSerializer):
    access_credential = AccessCredentialToScrapeSerializer()

    class Meta:
        model = Asset
        fields = ['ip', 'port', 'asset_type', 'access_credential']


class UserDefinedScriptToScrapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDefinedScript
        fields = ['name', 'language', 'code', 'output_type', 'fields', 'parameters']


class MonitorToScrapeSerializer(serializers.ModelSerializer):
    asset = AssetToScrapeSerializer()
    user_defined_script = UserDefinedScriptToScrapeSerializer()
    recipients = UserSerializer(many=True)

    class Meta:
        model = Monitor
        fields = ['name', 'asset',
                  'scrape_category', 'scrape_fields', 'scrape_parameters',
                  'user_defined_script',
                  'interval', 'report_time', 'report_list', 'recipients']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        recipients = ret['recipients']
        ret['recipients'] = [r['email'] for r in recipients]
        return ret
