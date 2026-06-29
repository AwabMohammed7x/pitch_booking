from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import *

# 🦸‍♂️ السطر المنقذ: عشان ديجانجو يعرف إن User هو الموديل المخصص اللي في accounts
User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'profile_pic', 'bio'] # حقول البروفايل بتاعك


class CustomUserSerializer(serializers.ModelSerializer):
    # 💥 هنا السحر (Nested Serializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']