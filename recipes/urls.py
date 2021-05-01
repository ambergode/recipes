from django.urls import path

from . import views

urlpatterns = [
    path('/<int:recipe_id>/', views.recipe_view, name="recipe_view"),
    path('/<int:recipe_id>/edit', views.edit_recipe, name="edit_recipe"),
    path('/edit_ingredients', views.edit_ingredients, name="edit_ingredients"),
    path('', views.index, name='index'),
]