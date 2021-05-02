from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('<int:recipe_id>/', views.detail, name="detail"),
    path('<int:recipe_id>/edit/', views.edit_recipe, name="edit_recipe"),
    path('', views.index, name='index'),
    path('shoppinglist/', views.list, name="list"),
    path('mealplanning/', views.planning, name="planning"),
]