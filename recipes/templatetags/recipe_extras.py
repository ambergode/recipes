from django import template

from ..models import Recipe, Favorites, Plan, Shop

register = template.Library()

@register.simple_tag
def get_status(tag, recipe_id, request):
    if request.user.is_authenticated:
        current_user = request.user
        recipe = Recipe.objects.get(pk = recipe_id)
        action_dict = {
            'plan': Plan,
            'shop': Shop,
            'fav': Favorites
        }
        action = action_dict[tag]
        if action.objects.filter(recipe = recipe, user = current_user).count() > 0:
            return True
        else:
            return False
    return False

