from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AccessCredentialSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['id', 'name', 'access_type']


class AssetListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_detail = UserSerializer(source='user', read_only=True)
    access_credential = serializers.PrimaryKeyRelatedField(
        queryset=AccessCredential.objects.all())
    access_credential_detail = AccessCredentialSerializerSimple(
        source='access_credential', read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'user', 'user_detail', 'name', 'ip', 'port', 'asset_type',
                  'access_credential', 'access_credential_detail', 'note', 'create_date']


class AssetCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    access_credential = serializers.PrimaryKeyRelatedField(
        queryset=AccessCredential.objects.all())

    class Meta:
        model = Asset
        fields = ['user', 'name', 'ip', 'port', 'asset_type',
                  'access_credential', 'note']

    def validate_name(self, value):
        user = self.initial_data.get('user')
        if Asset.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError(
                "Asset with this name already exists.")
        return value

    def validate_access_credential(self, value):
        user = self.initial_data.get('user')
        try:
            cred = AccessCredential.objects.get(name=value)
        except:
            raise serializers.ValidationError(
                "The Access Credential is not exist.")
        if user != cred.user.id:
            raise serializers.ValidationError(
                "The Access Credential is not yours.")
        return value


class AssetUpdateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    access_credential = serializers.PrimaryKeyRelatedField(
        queryset=AccessCredential.objects.all())

    class Meta:
        model = Asset
        fields = ['user', 'name', 'ip', 'port', 'asset_type',
                  'access_credential', 'note']

    def validate_name(self, value):
        user = self.initial_data.get('user')
        if Asset.objects.filter(user=user, name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                "Asset with this name already exists.")
        return value

    def validate_access_credential(self, value):
        user = self.initial_data.get('user')
        try:
            cred = AccessCredential.objects.get(name=value)
        except:
            raise serializers.ValidationError(
                "The Access Credential is not exist.")
        if user != cred.user.id:
            raise serializers.ValidationError(
                "The Access Credential is not yours.")
        return value


class AccessCredentialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['id', 'user', 'name', 'access_type',
                  'username', 'password', 'secret', 'note',
                  'create_date']


class AccessCredentialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['user', 'name', 'access_type',
                  'username', 'password', 'secret', 'note']

    def validate_name(self, value):
        user = self.initial_data.get('user')
        if AccessCredential.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError(
                "AccessCredential with this name already exists.")
        return value

    def validate_access_type(self, value):
        if ('_id_password') in value:
            if self.initial_data.get('username') == None or self.initial_data.get('password') == None:
                raise serializers.ValidationError(
                    "username and password field is required.")
        else:
            if self.initial_data.get('secret') == None:
                raise serializers.ValidationError(
                    "secret field is required.")
        return value

    def validate_username(self, value):
        if ('_id_password' in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")

    def validate_password(self, value):
        if ('_id_password' in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")

    def validate_secret(self, value):
        if ('_id_password' not in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")


class AccessCredentialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCredential
        fields = ['user', 'name', 'access_type',
                  'username', 'password', 'secret', 'note']

    def validate_name(self, value):
        user = self.initial_data.get('user')
        if AccessCredential.objects.filter(user=user, name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                "AccessCredential with this name already exists.")
        return value

    def validate_access_type(self, value):
        if ('_id_password') in value:
            if self.initial_data.get('username') == None or self.initial_data.get('password') == None:
                raise serializers.ValidationError(
                    "username and password field is required.")
        else:
            if self.initial_data.get('secret') == None:
                raise serializers.ValidationError(
                    "secret field is required.")
        return value

    def validate_username(self, value):
        if ('_id_password' in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")

    def validate_password(self, value):
        if ('_id_password' in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")

    def validate_secret(self, value):
        if ('_id_password' not in self.initial_data.get('access_type')) and not value:
            raise serializers.ValidationError("This field is required.")


class ScriptListSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Script
        fields = ['id', 'user', 'user_detail', 'name', 'note']


class ScriptRetrieveSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Script
        fields = ['id', 'user', 'user_detail', 'name',
                  'language', 'code', 'authority', 'output_type',
                  'note', 'create_date', 'update_date', 'revision']


class ScriptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = ['user', 'name', 'language', 'code',
                  'authority', 'output_type', 'note']

    def validate_name(self, value):
        model = self.Meta.model
        user = self.initial_data.get('user')
        if model.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError(
                "Script with this name already exists.")
        return value


class ScriptUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = ['user', 'name', 'language', 'code',
                  'authority', 'output_type', 'note']

    def validate_name(self, value):
        model = self.Meta.model
        user = self.initial_data.get('user')
        if model.objects.filter(user=user, name=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                "Script with this name already exists.")
        return value


class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = ['asset', 'target_system', 'scrap_code', 'interval',
                  'reporting', 'report_time', 'report_receiver']
