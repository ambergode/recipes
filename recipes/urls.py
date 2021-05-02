from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('<int:recipe_id>/', views.detail, name="detail"),
    path('<int:recipe_id>/edit', views.edit_recipe, name="edit_recipe"),
    path('edit_ingredients/', views.edit_ingredients, name="edit_ingredients"),
    path('', views.index, name='index'),
]