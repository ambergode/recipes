from django import template

import datetime

from ..models import Recipe, Favorites, Plan, Shop, ShoppingList, MealPlan, PlannedMeal

register = template.Library()

@register.simple_tag
def get_status(tag, model, recipe_id, request):
    if request.user.is_authenticated:
        current_user = request.user
        if model == 'recipe':
            model = Recipe
        elif model == 'mealplan':
            model = MealPlan
        else:
            model = ShoppingList
        recipe = model.objects.get(pk = recipe_id)
        
        action_dict = {
            'plan': Plan,
            'shop': Shop,
            'fav': Favorites
        }
        
        action = action_dict[tag]
        if model == Recipe:
            if action.objects.filter(recipe = recipe, user = current_user).count() > 0:
                return True
            else:
                return False
        elif model == MealPlan:
            if action.objects.filter(mealplan = recipe, user = current_user).count() > 0:
                return True
            else:
                return False
        else:
            if action.objects.filter(shopping_list = recipe, user = current_user).count() > 0:
                return True
            else:
                return False
    return False


@register.filter
def get_item(dictionary, key):
    try:
        key = int(key)
    except:
        pass

    return dictionary.get(key)

@register.filter
def plus_days(value, days):
    return value + datetime.timedelta(days=int(days))

@register.filter
def get_related(planned_meal, attribute):
    if attribute == 'recipes':
        return planned_meal.recipes.all()
    elif attribute == 'ingredients':
        return planned_meal.ingredients.all()
