from django.shortcuts import render
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from users.models import User
from api.serializers import UserSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
