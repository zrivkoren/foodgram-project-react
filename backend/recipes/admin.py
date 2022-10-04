from django.contrib import admin

from .models import Ingredient, Recipe, Tag, IngredientsInRecipe

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)

@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text',)
    list_filter = ('author',)

@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)

