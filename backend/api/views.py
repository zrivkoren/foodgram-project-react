from django.shortcuts import render
from rest_framework import viewsets
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from users.models import User
from recipes.models import Tag, Ingredient, Recipe, IngredientsInRecipe

from api.serializers import UserSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
