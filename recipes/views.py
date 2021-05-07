from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
import json

from .models import Recipe, Ingredient, Ingredient, Step
from .models import VOLUME, WEIGHT, UNIT
from .convert_units import convert_units

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
        if request.POST["search"]:
            q_args = ""
            for char in request.POST["search"]:
                q_args += char
            return HttpResponseRedirect(reverse("recipes:index"))
        else:
            return HttpResponseRedirect(reverse("recipes:index"))
    else:
        if request.GET.get("q") == None:
            recipe_list = Recipe.objects.order_by('-name')
            context = {
                'recipe_list': recipe_list,
            }
        else:
            recipe_list = Recipe.objects.filter(name__icontains=request.GET.get("q"))
            q = request.GET.get("q")
            context = {
                'recipe_list': recipe_list,
                "q": q,
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


def create_recipe(request):
    # TODO
    return render(request, 'recipes/create_recipe.html', {})


def edit_recipe(request, recipe_id):
    # TODO
    return HttpResponse("TODO")

def edit_ingredients(request):
    # TODO
    return HttpResponse("TODO")    


def shopping(request):
    recipes = Recipe.objects.filter(in_shopping=True)

    # create empty dictionary for shopping list
    shopping_list = {}
    for recipe in recipes:
        # get ingredients of each recipe
        ingquants = recipe.get_ingquants()
        for ingquant in ingquants:
            # check if ingredients already in dictionary
            if ingquant.ingredient in shopping_list.keys():
                # if in dictionary already, check if units match
                if shopping_list[ingquant.ingredient][1] != ingquant.unit:
                # if units don't match, complete correct conversion    
                    ingquant = convert_units(ingquant.quantity, ingquant.unit, shopping_list[ingquant.ingredient][1])
                # add quantities to dictionary
                shopping_list[ingquant.ingredient][0] += ingquant.quantity
            # if not in dictionary already, add ingredient and tuple for quantity and unit
            else:
                shopping_list[ingquant.ingredient] = [ingquant.quantity, ingquant.unit]

    return render(request, 'recipes/shopping.html', {"shopping_list": shopping_list})

def planning(request):
    return HttpResponse("TODO")

