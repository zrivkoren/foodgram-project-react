from rest_framework import viewsets
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from http import HTTPStatus
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse

from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from users.models import User, Subscribe
from recipes.models import (
    Tag, Ingredient, Recipe, IngredientsInRecipe, Favorite, ShoppingCart
)
from api.serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, RecipeCreateSerializer, RecipeReadSerializer,
    FavoriteCartSerializer, SubscribeSerializer
)
from .filters import RecipeFilter, IngredientFilter


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    additional_serializer = SubscribeSerializer

    @action(
        methods=['GET'], detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        authors = Subscribe.objects.filter(user=user)
        page = self.paginate_queryset(authors)
        serializer = self.additional_serializer(
            page,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {
                        'errors': 'Нельзя подписаться на самого себя'
                    }, status=HTTPStatus.BAD_REQUEST
                )
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=HTTPStatus.BAD_REQUEST
                )
            subscribe = Subscribe.objects.create(user=user, author=author)
            serializer = self.additional_serializer(
                subscribe, context={'request': request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if request.method == 'DELETE':
            if user == author:
                return Response(
                    {'errors': 'Пользователь и автор совпадают'},
                    status=HTTPStatus.BAD_REQUEST
                )
            follow = Subscribe.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=HTTPStatus.BAD_REQUEST
            )


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
    additional_serializer = FavoriteCartSerializer

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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request, kwargs.get('pk'))

    @action(
        detail=True,
        methods=['GET', 'POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, kwargs.get('pk'))

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        filename = f'{user.username}_shopping_list.txt'
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_sum=Sum('amount')
        )
        shopping_cart_tmp = {}
        for ingredient in ingredients:
            name = ingredient[0]
            shopping_cart_tmp[name] = {
                'amount': ingredient[2],
                'measurement_unit': ingredient[1]
            }
            shopping_cart = ["Список продуктов к покупке:\n"]
            for key, value in shopping_cart_tmp.items():
                shopping_cart.append(f'{key} - {value["amount"]} '
                                     f'{value["measurement_unit"]}\n')
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={filename}.txt'
        )
        return response
