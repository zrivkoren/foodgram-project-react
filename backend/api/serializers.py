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
        models = Ingredient
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


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    ingredients = IngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_in_recipe'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'tags', 'ingredients', 'image', 'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    ingredients = IngredientsInRecipeSerializer(
        source='ingredients_in_recipe',
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'tags', 'ingredients', 'image', 'text',
            'cooking_time',
        )

    def ingredients_create(self, ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            recipe_ingredient = IngredientsInRecipe(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']
                ),
                recipe=recipe,
                amount=amount
            )
            ingredients_list.append(recipe_ingredient)
        IngredientsInRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe')
        image = validated_data.pop('image')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.ingredients_create(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients_in_recipe')
        tags = validated_data.pop('tags')
        self.ingredients_create(ingredients=ingredients, recipe=instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, attrs):
        ingredients = attrs.get('ingredients_in_recipe')
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
        return attrs
