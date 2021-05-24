from django import template

from ..models import Recipe, Favorites, Plan, Shop, ShoppingList

register = template.Library()

@register.simple_tag
def get_status(tag, model, recipe_id, request):
    if request.user.is_authenticated:
        current_user = request.user
        if model == 'recipe':
            model = Recipe
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
        else:
            if action.objects.filter(shopping_list = recipe, user = current_user).count() > 0:
                return True
            else:
                return False
    return False


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
