from django.urls import path

from . import views

app_name = 'recipes'
urlpatterns = [
    path('', views.index, name='index'),

    path('<int:recipe_id>/', views.detail, name="detail"),
    
    path('create/<str:creation>', views.create, name="create_recipe"),
    path('<int:recipe_id>/edits_recorded/', views.record_edit_recipe, name="edit_recipe"),
    path('<int:recipe_id>/edit/', views.display_edit_recipe, name="display_edit_recipe"),
    path('<int:recipe_id>/edit/add_ing_to_list/', views.add_ing_to_list, name="add_ing_to_list"),
    path('<int:recipe_id>/edit/delete_ing/', views.delete_ing, name="delete_ing"),
    path('<int:recipe_id>/delete_recipe/', views.delete_recipe, name="delete_recipe"),

    path('add_ingredient/', views.add_ingredient, name="add_ingredient"),
    path('update_ingredients/', views.update_ingredients, name="update_ingredients"),

    path('shoppinglist/', views.shopping, name="shopping"),
    path('<int:recipe_id>/update_shopping_list/', views.update_shopping_list, name='update_shopping_list'),
    path('<int:recipe_id>/update_shopping_list/add_ing_to_list/', views.add_ing_to_list, name='add_ing_to_list'),
    path('<int:recipe_id>/update_shopping_list/delete_ing/', views.delete_ing, name='delete_ing'),
    path('<int:recipe_id>/record_shopping_list/', views.record_shopping_list, name='record_shopping_list'),
    path('<int:recipe_id>/shopping_list/', views.detail_shopping_list, name='detail_shopping_list'),
    path('all_shopping_lists/', views.index_shopping_lists, name='index_shopping_lists'),
    path('<int:recipe_id>/delete_list/', views.delete_list, name="delete_list"),
    
    path('mealplanning/', views.planning, name="planning"),
    path('create_plan/', views.create_plan, name='create_plan'),
    path('<int:plan_id>/update_plan/', views.update_plan, name='update_plan'),
    path('<int:plan_id>/edit_plan/update_plan/', views.update_plan, name='update_plan'),
    path('<int:plan_id>/edit_plan/update_plan_ajax/', views.update_plan_ajax, name='update_plan_ajax'),
    path('<int:plan_id>/edit_plan/', views.display_edit_plan, name='display_edit_plan'),
    path('<int:plan_id>/edit_plan/update_and_edit_plan/', views.update_and_edit_plan, name='update_and_edit_plan'),
    path('<int:plan_id>/edit_plan/add_base_meals/', views.add_base_meals, name='add_base_meals'),
    path('<int:plan_id>/edit_plan/update_days/', views.update_days, name='update_days'),
    path('<int:plan_id>/edit_plan/list_recipes/', views.list_recipes, name='list_recipes'),
    path('<int:plan_id>/edit_plan/add_recipe/', views.plan_add_recipe, name='plan_add_recipe'),
    path('mealplanning/<int:plan_id>', views.plan_detail, name='plan_detail'),
    path('record_planned_meal/', views.record_planned_meal, name='record_planned_meal'),
    path('all_plans/', views.index_plans, name='index_plans'),
    path('<int:plan_id>/delete_plan/', views.delete_plan, name='delete_plan'),
    path('<int:plan_id>/bulk_add', views.bulk_add, name='bulk_add'),

    path('button_ajax/', views.button_ajax, name="button_ajax"),
    path('cancel/', views.cancel, name='cancel'),
]