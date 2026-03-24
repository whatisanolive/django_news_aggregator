from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.CharField(source='profile.profile_pic', read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_pic"]
