from django.shortcuts import get_object_or_404
from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, IngredientsInRecipe, Recipe
from users.models import User


class UserSerializer(DjoserUserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredientsinrecipe_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time', 'id', 'ingredients'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Recipe.objects.filter(
            shopping_cart__user=user,
            id=obj.id
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(use_url=True)
    ingredients = IngredientsInRecipeSerializer(
        source='ingredientsinrecipe_set',
        many=True
    )
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time', 'id', 'ingredients'
        )

    def ingredients_create(self, ingredients, recipe):
        ingredients_list = [
            IngredientsInRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientsInRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientsinrecipe_set')
        image = validated_data.pop('image')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.ingredients_create(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredientsinrecipe_set')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        self.ingredients_create(ingredients=ingredients, recipe=instance)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredientsinrecipe_set')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент в рецепте'
            })
        valid_ingredients = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            if amount == 0:
                raise serializers.ValidationError({
                    'ingredients': 'Количество должно быть больше 0'
                })
            if ingredient in valid_ingredients:
                raise serializers.ValidationError({
                    'ingredients': 'Такой ингредиент уже есть в рецепте'
                })
            valid_ingredients.append(ingredient)
        return data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Recipe.objects.filter(
            shopping_cart__user=user,
            id=obj.id
        ).exists()


class FavoriteCartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
