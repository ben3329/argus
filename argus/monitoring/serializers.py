from rest_framework import serializers
from .models import Assets


class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = ['user', 'name', 'access_type']