from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader

from .models import Recipe, Ingredient, Ingredient, Step

def index(request):
    recipe_list = Recipe.objects.order_by('-name')
    context = {
        'recipe_list': recipe_list
    }
    return render(request, "recipes/index.html", context)


def detail(request, recipe_id):
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