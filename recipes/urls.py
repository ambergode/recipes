from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('<int:recipe_id>/', views.detail, name="detail"),
    path('<int:recipe_id>/edit/', views.edit_recipe, name="edit_recipe"),
    path('', views.index, name='index'),
    path('shoppinglist/', views.shopping, name="shopping"),
    path('mealplanning/', views.planning, name="planning"),
    path('createrecipe/', views.create_recipe, name="create_recipe"),
]