from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer

from users.models import User

class UserSerializer(DjoserUserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
