from django_filters import FilterSet, CharFilter, AllValuesMultipleFilter

from recipes.models import Recipe, Ingredient

class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith',)

    class Meta:
        model = Ingredient
        fields = ('name',)

class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)