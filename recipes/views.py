from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Recipe, Ingredient, Ingredient, Step

def log_lists(request):
    recipe_id = request.POST["recipe_id"]
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    try:
        request.POST["list_toggle"]
        if recipe.in_shopping == True:
            recipe.in_shopping = False
        else:
            recipe.in_shopping = True
    except:
        try:
            request.POST["plan_toggle"]
            if recipe.in_planning == True:
                recipe.in_planning = False
            else:
                recipe.in_planning = True
        except:
            return HttpResponse("Error in recording list selection.")
    
    recipe.save()
    return recipe

def index(request):
    if request.method == "POST":
        log_lists(request)
        return HttpResponseRedirect(reverse("recipes:index"))
    else:
        recipe_list = Recipe.objects.order_by('-name')
        context = {
            'recipe_list': recipe_list
        }
        return render(request, "recipes/index.html", context)


def detail(request, recipe_id):
    if request.method == "POST":
        recipe = log_lists(request)
        return HttpResponseRedirect(reverse("recipes:detail", args=(recipe.id,)))
    else:
        recipe = get_object_or_404(Recipe, pk = recipe_id)
        steps = recipe.get_steps()
        ingredients = recipe.get_ingquants()
        total = recipe.get_total_time()
        return render(request, 'recipes/detail.html', {
            'recipe': recipe, 
            'steps': steps, 
            'ingredients': ingredients,
            'total': total,
            })


def edit_recipe(request, recipe_id):
    # TODO
    return HttpResponse("TODO")


def edit_ingredients(request):
    # TODO
    return HttpResponse("TODO")

def list(request):
    return HttpResponse("TODO")

def planning(request):
    return HttpResponse("TODO")