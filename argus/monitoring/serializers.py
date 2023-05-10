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


class AssetViewSetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_detail = UserSerializer(source='author', read_only=True)
    access_credential = serializers.PrimaryKeyRelatedField(
        queryset=AccessCredential.objects.all())
    access_credential_detail = AccessCredentialSerializerSimple(
        source='access_credential', read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'author', 'author_detail', 'name', 'ip', 'port', 'asset_type',
                  'access_credential', 'access_credential_detail', 'note', 'create_date']
        read_only_fields = ['author_detail', 'access_credential_detail', 'create_date'] 


class AccessCredentialViewSetSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = AccessCredential
        fields = ['id', 'author', 'author_detail', 'name', 'access_type',
                  'username', 'password', 'secret', 'note',
                  'create_date']
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

    def validate_secret(self, value):
        if ('_password' not in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")


class ScriptListSerializer(serializers.ModelSerializer):
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = UserDefinedScript
        fields = ['id', 'author', 'author_detail', 'name', 'note']


class ScriptRetrieveSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = UserDefinedScript
        fields = ['id', 'author', 'user_detail', 'name',
                  'language', 'code', 'authority', 'output_type',
                  'note', 'create_date', 'update_date', 'revision']


class ScriptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDefinedScript
        fields = ['author', 'name', 'language', 'code',
                  'authority', 'output_type', 'note']

    def validate_name(self, value):
        model = self.Meta.model
        author = self.initial_data.get('author')
        if model.objects.filter(author=author, name=value).exists():
            raise serializers.ValidationError(
                "Script with this name already exists.")
        return value


class ScriptUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDefinedScript
        fields = ['author', 'name', 'language', 'code',
                  'authority', 'output_type', 'note']

    def validate_name(self, value):
        model = self.Meta.model
        author = self.initial_data.get('author')
        if model.objects.filter(author=author, name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                "Script with this name already exists.")
        return value


# For scrape client
class AccessCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['access_type', 'username', 'password', 'secret']


class AssetSerializer(serializers.ModelSerializer):
    access_credential = AccessCredentialSerializer()

    class Meta:
        model = Asset
        fields = ['ip', 'port', 'asset_type', 'access_credential']


class BuiltInScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuiltInScript
        fields = ['category', 'fields', 'parameter']


class UserDefinedScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDefinedScript
        fields = ['name', 'language', 'code', 'output_type']


class MonitorToScrapeSerializer(serializers.ModelSerializer):
    asset = AssetSerializer()
    script = serializers.SerializerMethodField()
    recipients = UserSerializer(many=True)

    class Meta:
        model = Monitor
        fields = ['name', 'asset', 'script', 'interval',
                  'report_list', 'report_time', 'recipients']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        recipients = ret['recipients']
        ret['recipients'] = [r['email'] for r in recipients]
        return ret

    def get_script(self, obj):
        if obj.user_defined_script:
            return UserDefinedScriptSerializer(obj.user_defined_script).data
        elif obj.built_in_script:
            return BuiltInScriptSerializer(obj.built_in_script).data
