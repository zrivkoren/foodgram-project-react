from django.shortcuts import render
from rest_framework import viewsets
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly
    # , IsAuthenticated,
)
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from http import HTTPStatus
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from users.models import User
from recipes.models import Tag, Ingredient, Recipe, IngredientsInRecipe

from api.serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, RecipeCreateSerializer, RecipeReadSerializer,
    FavoriteCartSerializer
)
from .filters import RecipeFilter, IngredientFilter


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'PUT'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
                recipe=recipe, user=request.user
        ).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = FavoriteCartSerializer(recipe)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            model.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.BAD_REQUEST)
