from django_filters import (
    FilterSet, CharFilter, AllValuesMultipleFilter, ModelChoiceFilter
)

from users.models import User
from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith', )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
