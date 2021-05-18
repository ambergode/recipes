from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),
    path('all_recipes/', views.index_all, name='index_all'),
    path('<int:recipe_id>/', views.detail, name="detail"),
    path('<int:recipe_id>/edits_recorded/', views.record_edit_recipe, name="edit_recipe"),
    path('<int:recipe_id>/edit/', views.display_edit_recipe, name="display_edit_recipe"),
    path('shoppinglist/', views.shopping, name="shopping"),
    path('mealplanning/', views.planning, name="planning"),
    path('create_recipe/', views.create_recipe, name="create_recipe"),
    path('add_ingredient/', views.add_ingredient, name="add_ingredient"),
    path('button_ajax/', views.button_ajax, name="button_ajax"),
    path('update_ingredients/', views.update_ingredients, name="update_ingredients"),
    path('<int:recipe_id>/delete_recipe/', views.delete_recipe, name="delete_recipe"),
    path('cancel/', views.cancel, name='cancel'),
]