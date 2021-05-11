from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:recipe_id>/', views.detail, name="detail"),
    path('<int:recipe_id>/edits_recorded/', views.record_edit_recipe, name="edit_recipe"),
    path('<int:recipe_id>/edit/', views.display_edit_recipe, name="display_edit_recipe"),
    path('shoppinglist/', views.shopping, name="shopping"),
    path('mealplanning/', views.planning, name="planning"),
    path('create_recipe/', views.create_recipe, name="create_recipe"),
    path('add_ingredient/', views.add_ingredient, name="add_ingredient"),
]