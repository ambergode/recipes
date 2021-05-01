from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Recipe, Ingredient, Ingredient, Step

def index(request):
    recipe = get_object_or_404(Recipe, pk=Recipe.id)
    context = {
        'recipe_list': recipe_list,
    }
    return render(request, "recipes/index.html", {'recipe': recipe})


def recipe_view(request, recipe_id):
    # TODO
    return HttpResponse("TODO")


def edit_recipe(request, recipe_id):
    # TODO
    return HttpResponse("TODO")


def edit_ingredients(request):
    # TODO
    return HttpResponse("TODO")