from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator

import json
from datetime import datetime, timezone, timedelta

from .models import Recipe, Ingredient, IngQuant, Step, Favorites, Shop, Plan, ShoppingList, MealPlan, PlannedMeal
from .models import VOLUME, WEIGHT, UNIT, UNIT_CHOICES, MEAL_CHOICES, MEALTIME_CHOICES, CATEGORY_CHOICES, UNIT_DICT, CATEGORY_DICT
from .convert_units import convert_units, get_smaller_unit
from .forms import MealForm, UnitForm, CategoryForm, RecipePhotoForm

# Utility functions

def normalize(data):
    return data.strip().lower()


def query_shopping_lists(request):
    shopping_lists = []
    
    if request.GET.get("q") == None:
        lists = ShoppingList.objects.filter(user = request.user).order_by('-name')
    else:
        lists = ShoppingList.objects.filter(name__icontains=request.GET.get("q"), user = request.user)

    for each in lists:
        ingquants = each.get_ingquants()
        ingredients = []
        for ingquant in ingquants:
            ingredients.append(ingquant)
        shopping_lists.append([each, ingredients])
    return shopping_lists


def ajax(request, template, ctx):
    template = loader.get_template(template)
    html = template.render(ctx, request)
    data_dict = {
        "html_from_view": html, 
        'success': True,
    }
    return JsonResponse(data=data_dict, safe=False)


def personalize_if_user_not_owner(requesting_user, recipe):
    if requesting_user != recipe.user:
        search = Recipe.objects.filter(user = requesting_user).filter(name = recipe.name.lower()).filter(personalized = True)
        # check if this personalized recipe is already in the database
        if search.count() == 1:    # if it is
            return  search[0]
            
        elif search.count() == 0:   # if it's not in the database already
            # create a new instance of this recipe tied to the user
            ingquants = IngQuant.objects.filter(recipe = recipe)
            recipe.pk = None
            recipe.save()
            for instance in ingquants:
                instance.pk = None
                instance.recipe = recipe
                instance.save()
            recipe.user = requesting_user
            recipe.personalized = True
            recipe.public = False
            recipe.save()
            return recipe
        else: # it's somehow gotten into the database too many times
            return -1
    else: 
        return recipe


def get_components(recipe):
    components = []
    ingquants = recipe.get_ingquants()
    for ingquant in ingquants:
        form = UnitForm(initial={'choose_unit': ingquant.unit.upper()}, prefix="name_" + str(ingquant.id))
        components.append((ingquant, form))
    return components


@login_required
def button_ajax(request):
    return_data = {'success': False} 
    if request.method=='POST':
        data = json.loads(request.body)
        model = data.get('model')
        if model == 'shopping_list':
            model_update = ShoppingList
        else:
            model_update = Recipe
        recipe_id = data.get('recipe_id')
        recipe = model_update.objects.get(pk = recipe_id)
        action = data.get('tag')
        action_dict = {
            'shop': Shop,
            'plan': Plan,
            'favorite': Favorites 
        }

        user = request.user
        model = action_dict[action]
        
        if model_update == ShoppingList:
            match = model.objects.filter(shopping_list = recipe, user = user)
        else:
            match = model.objects.filter(recipe = recipe, user = user)

        if match.count() == 0:
            inst = model()
            if model_update == ShoppingList:
                inst.shopping_list = recipe
            else:
                inst.recipe = recipe
            inst.user = user
            inst.save()
            return_data['success'] = True
            return_data['action'] = "add"
        else:
            inst = match[0]
            inst.delete()
            return_data['success'] = True
            return_data['action'] = "remove"
    
        source = data.get('source')
        if source == 'shopping':
            template = loader.get_template('recipes/current_shopping_list.html')
            context = get_shopping_context(request)
            html = template.render(context, request)
            return_data["html_from_view"] = html
            return JsonResponse(data=return_data, safe=False)
        else:
            return JsonResponse(return_data)
    else: 
        return HttpResponse("Something went wrong recording your button click on " + action)


# Page views

def index(request, model_name='recipe'):
    
    # choose the model
    if model_name == "shopping_list":
        model = ShoppingList
    else:
        model = Recipe

    # set the recipe_list to render
    if not request.user.is_authenticated:
        recipe_list = model.objects.filter(public = True).order_by('-name')
    else:
        user = request.user
        
        recipe_list = model.objects.filter(user=user).order_by('-name')
        
        # parse data if this is a fetch request
        if request.is_ajax():
            data = json.loads(request.body)
        else:
            data = {}

        q_filter = data.get('radio')
        # basic list already has 'mine' filter
        if q_filter == None: q_filter = 'mine'
        
        if q_filter == 'mine':
            recipe_list = model.objects.filter(user = user).order_by('-name')
        elif q_filter == 'all':
            recipe_list = model.objects.filter(Q(user = user) | Q(public = True)).order_by('-name')
        elif q_filter == 'public':
            recipe_list = model.objects.filter(public = True).order_by('-name')
        elif q_filter == 'favorites':
            favorites = Favorites.objects.filter(user = user)
            pks = []
            for favorite in favorites:
                pks.append(favorite.recipe.id)
            recipe_list = model.objects.filter(pk__in = pks)

    if data.get("q") != None:
        recipe_list = recipe_list.filter(name__icontains=data.get("q").lower())

    ctx = {}

    if model_name == 'shopping_list':
        ctx['shopping_lists'] = query_shopping_lists(request)
    else:
        ctx['recipe_list'] = recipe_list
    
    if request.is_ajax():
        return ajax(request, 'recipes/index_cards.html', ctx)

    return render(request, "recipes/index.html", ctx) 


def detail(request, recipe_id):

    def record_nutrient_value(nutrient, ingredient, in_grams, nutrition):
        # nutrient values stored in database as g or mg per 100g
        nutrient_value = getattr(ingquant.ingredient, nutrient)
        # calculate the value of that nutrient in that recipe
        # multiply converted inquant quantity by the nutrient/100g
        value = float(in_grams) * float(nutrient_value) / 100.0
        # add value to nutrition
        nutrition[nutrient] += value
        # If an ingredient belongs to a user, add a note that the nutrition information is not verified
        if ingquant.ingredient.user != None:
            if ingquant.ingredient not in unverified:
                unverified.append(ingquant.ingredient)
        return value

    if request.method == "POST":
        return HttpResponseRedirect(reverse("recipes:detail", kwargs= {"recipe_id": recipe_id,}))
    else:
        recipe = get_object_or_404(Recipe, pk = recipe_id)

        nutrition = {
            'calories': 0,
            'fat': 0,
            'satfats': 0,
            'transfats': 0, 
            'monounsatfats': 0,
            'polyunsatfats': 0, 
            'cholesterol': 0, 
            'sodium': 0,
            'carbs': 0,
            'fiber': 0,
            'sugar': 0,
            'protein': 0,
        }
        uncounted = []
        unverified = []

        ingquants = recipe.get_ingquants()
        ingquantsAndUnits = []
        for ingquant in ingquants:
            unit = ingquant.unitDisplay()
            ingquantsAndUnits.append((ingquant, unit))
            # get nutrition information and add to total
            for nutrient in nutrition.keys(): # for each nutrient in nutrition
                # convert ingquant quantity to grams
                in_grams = convert_units(ingquant.quantity, ingquant.unit, "g") 
                # if convert_unit returns -1, conversion not possible
                if in_grams <= 0 and ingquant.ingredient.weight_per_serving != 0 and ingquant.ingredient.weight_per_serving != None:
                    # get typical serving information
                    serving_unit = ingquant.ingredient.typical_serving_unit
                    serving_quantity =ingquant.ingredient.typical_serving_size
                    serving_grams = ingquant.ingredient.weight_per_serving
                    # check if typical serving unit can be converted to the unit in the recipe
                    convert_to_typical_serving_unit = convert_units(ingquant.quantity, ingquant.unit, serving_unit)
                    if convert_to_typical_serving_unit > 0:
                        # convert_to_typical_serving_unit value: quantity in typical serving unit
                        in_grams = (float(convert_to_typical_serving_unit) * float(serving_grams)) / float(serving_quantity)
                        record_nutrient_value(nutrient, ingquant.ingredient, in_grams, nutrition)
                    # if serving_grams is zero or does not exist, no conversion is possible
                    else:
                        # add to list of uncounted ingredients
                        if ingquant.ingredient not in uncounted:
                            uncounted.append(ingquant.ingredient)
                        # means the units are not compatible, so no reason to keep going with this one
                        break
                else:
                    record_nutrient_value(nutrient, ingquant.ingredient, in_grams, nutrition)
        
        # divide total nutrition by number of servings
        servings = recipe.servings
        for nutrient in nutrition.keys():
            nutrition[nutrient] /= servings      

        ctx = {
            'recipe': recipe,
            'steps': recipe.get_steps(),
            'ingredients': ingquantsAndUnits,
            'total': recipe.get_total_time(),
            'nutrition': nutrition,
            'uncounted': uncounted,
            'unverified': unverified,
        }

        return render(request, 'recipes/detail.html', ctx)


@login_required
def create(request, creation):
    if request.method == "POST":
        new_recipe = request.POST.get("recipe_name")
        if request.POST.get('model') == 'recipe':
            model = Recipe
        else:
            model = ShoppingList
        if new_recipe != None:
            new_recipe = new_recipe.lower().strip()
            
            # Check to make sure name is unique
            if model.objects.filter(name = new_recipe, user = request.user).count() > 0:
                ctx = {
                    "error_message": "You already have something called " + new_recipe + ". Please use a unique name ",
                    "recipe": model.objects.filter(name = new_recipe, user = request.user)[0]
                }
                return render(request, 'recipes/create_recipe.html', ctx) 
                
            # if unique, create new recipe    
            else:
                add_recipe = model()
                add_recipe.name = new_recipe
                add_recipe.user = request.user
                add_recipe.save()
        if model == Recipe:     
            return HttpResponseRedirect(reverse("recipes:display_edit_recipe", kwargs= { "recipe_id": add_recipe.id, }))
        else: 
            return HttpResponseRedirect(reverse("recipes:update_shopping_list", kwargs= { "recipe_id": add_recipe.id, }))
    else:
        return render(request, 'recipes/create_recipe.html', {'model': creation})


@login_required
def display_edit_recipe(request, recipe_id):
    return display_edit(request, recipe_id, 'recipe')


@login_required
def record_edit_recipe(request, recipe_id):
    return record_edit(request, recipe_id, Recipe)


@login_required
def add_ingredient(request, ingredient_id = None, source = 'recipe'):

    def add_ingredient_helper(ing_id, ing, recipe, request):

        if request.POST.get('category' + '_' + str(ing_id)) != None:
            key = request.POST.get('category' + '_' + str(ing_id))
            ing.category = CATEGORY_DICT[key]
        if request.POST.get('unit' + '_' + str(ing_id)) != None:
            ing.typical_serving_unit = request.POST.get('unit' + '_' + str(ing_id))
        if request.POST.get('serving_size' + '_' + str(ing_id)) != None:
            ing.typical_serving_size = request.POST.get('serving_size' + '_' + str(ing_id))
        if request.POST.get('weight_per_serving' + '_' + str(ing_id)) != None:
            ing.weight_per_serving = request.POST.get('weight_per_serving' + '_' + str(ing_id))
        
        if request.POST.get('protein' + '_' + str(ing_id)) != None:
            ing.protein = request.POST.get('protein' + '_' + str(ing_id))
        if request.POST.get('fat' + '_' + str(ing_id)) != None:
            ing.fat = request.POST.get('fat' + '_' + str(ing_id))
        if request.POST.get('carbs' + '_' + str(ing_id)) != None:
            ing.carbs = request.POST.get('carbs' + '_' + str(ing_id))
        if request.POST.get('calories' + '_' + str(ing_id)) != None:
            ing.calories = request.POST.get('calories' + '_' + str(ing_id))
        if request.POST.get('sugar' + '_' + str(ing_id)) != None:
            ing.sugar = request.POST.get('sugar' + '_' + str(ing_id))
        if request.POST.get('fiber' + '_' + str(ing_id)) != None:
            ing.fiber = request.POST.get('fiber' + '_' + str(ing_id))
        if request.POST.get('sodium' + '_' + str(ing_id)) != None:
            ing.sodium = request.POST.get('sodium' + '_' + str(ing_id))
        if request.POST.get('cholesterol' + '_' + str(ing_id)) != None:
            ing.cholesterol = request.POST.get('cholesterol' + '_' + str(ing_id))
        if request.POST.get('transfats' + '_' + str(ing_id)) != None:
            ing.transfats = request.POST.get('transfats' + '_' + str(ing_id))
        if request.POST.get('satfats' + '_' + str(ing_id)) != None:
            ing.satfats = request.POST.get('satfats' + '_' + str(ing_id))
        if request.POST.get('monounsatfats' + '_' + str(ing_id)) != None:
            ing.monounsatfats = request.POST.get('monounsatfats' + '_' + str(ing_id))
        if request.POST.get('polyunsatfats' + '_' + str(ing_id)) != None:
            ing.polyunsatfats = request.POST.get('polyunsatfats' + '_' + str(ing_id))

        ing.user = request.user
        
        ing.save()
        return ing

    # identify the recipe
    recipe_id = request.POST.get('recipe_id')
    model = source
    if model == 'shopping_list':
        recipe = ShoppingList.objects.get(pk = recipe_id)
    else:
        recipe = Recipe.objects.get(pk = recipe_id)
    
    # initialize variables
    quantity = 0
    unit = 'gram'

    if ingredient_id != None:
        ingredient_name = request.POST['add_ingredient_name_' + ingredient_id].strip().lower()
        # identify the initial ingquant from the recipe
        if model == 'shopping_list':
            ingquant = IngQuant.objects.filter(shopping_list = recipe, ingredient = ingredient_id)
        else:
            ingquant = IngQuant.objects.filter(recipe = recipe, ingredient = ingredient_id)
        if len(ingquant) > 0:
            # make sure to transfer quantity from prior inquant
            quantity = ingquant[0].quantity
            unit = ingquant[0].unit
        # delete old inquant
        ingquant.delete()
    else:
        ingredient_name = request.POST['add_ingredient_name_new'].strip().lower()
    
    # personalize ingredient name
    personalized_ingredient_name = "my " + ingredient_name
    added_ingredient = None

    # check to see if the ingredient name is in the database
    if Ingredient.objects.filter(ingredient = ingredient_name).count() != 0:
        ing_id = Ingredient.objects.filter(ingredient = ingredient_name)[0].id
        # if the ingredient name is not yet personalized
        # create a new personalized object
        if ingredient_name[0:3] != 'my ':
            ingredient_name = "my " + ingredient_name
            # if that name doesn't exist already, create it
            if Ingredient.objects.filter(ingredient = ingredient_name).count() == 0:
                ingredient = Ingredient(ingredient = ingredient_name)
            else: 
                # get the already personalized object
                ingredient = Ingredient.objects.filter(ingredient = ingredient_name)[0]
        else:
            # get the already personalized object
            ingredient = Ingredient.objects.filter(ingredient = ingredient_name)[0]
        added_ingredient = add_ingredient_helper(ing_id, ingredient, recipe, request)
    # check to see if the personalized name is in the database
    elif Ingredient.objects.filter(ingredient = personalized_ingredient_name).count() != 0:
        ing_id = Ingredient.objects.filter(ingredient = personalized_ingredient_name)[0].id
        # if the personalized ingredient already exists in the system
        ingredient = Ingredient.objects.filter(ingredient = personalized_ingredient_name)[0]
        added_ingredient = add_ingredient_helper(ing_id, ingredient, recipe, request)
    # otherwise create a new ingredient
    else:
        ingredient = Ingredient(ingredient = ('my ' + ingredient_name))
        added_ingredient = add_ingredient_helper('new', ingredient, recipe, request)

    components_ingredients = []
    for component in recipe.get_ingquants():
        components_ingredients.append(component.ingredient.id)

    # create a new ingquant
    if added_ingredient.id not in components_ingredients:
        new_ingquant = IngQuant(
            ingredient = added_ingredient, 
            quantity = quantity,
            unit = unit,
            )
        if source == 'shopping_list':
            new_ingquant.shopping_list = ShoppingList.objects.get(pk=recipe_id)
        else:
            new_ingquant.recipe = Recipe.objects.get(pk=recipe_id)
        new_ingquant.save()
    else:
        if model == 'shopping_list':
            update_ingquant = IngQuant.objects.filter(ingredient = added_ingredient.id, shopping_list = recipe)[0]
        else:
            update_ingquant = IngQuant.objects.filter(ingredient = added_ingredient.id, recipe = recipe)[0]
        update_ingquant.quantity = quantity
        update_ingquant.unit = unit
        update_ingquant.save()

    if source == 'shopping_list':
        return HttpResponseRedirect(reverse("recipes:update_shopping_list", args=(recipe_id,)))
    else:
        return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe_id,)))


def get_shopping_context(request):
    def shopping_helper(ingquant, check_ings, list_ingredients):
        ''' 
        Takes an ingquant, a list of ingquants to compare to, 
        and a dictionary of ingredients with key - name of ingredient and value of the ingquants with that ingredient name
        returns the updated dictionary
        '''

        # base case
        check_ings_names = []
        for ing in check_ings:
            check_ings_names.append(ing.ingredient.ingredient)

        if str(ingquant.ingredient) not in check_ings_names:
            list_ingredients[str(ingquant.ingredient)].append(ingquant)
        else:
            ing = check_ings[0]
            smaller = get_smaller_unit(ing.unit, ingquant.unit)

            if smaller == ing.unit.lower():
                convert_quantity = convert_units(ing.quantity, ing.unit, ingquant.unit)
                new_ingquant = IngQuant()
                new_ingquant.quantity = round(float(ingquant.quantity) + float(convert_quantity), 2) 
                new_ingquant.unit = ingquant.unit
                
            elif smaller == ingquant.unit.lower():
                convert_quantity = convert_units(ingquant.quantity, ingquant.unit, ing.unit)
                new_ingquant = IngQuant()
                new_ingquant.quantity = round(float(ing.quantity) + convert_quantity, 2)
                new_ingquant.unit = ing.unit
            
            if smaller == -1 or convert_quantity == -1:
                # cannot compare
                # remove current ing
                check_ings.remove(check_ings[0])
                # recurse
                return shopping_helper(ingquant, check_ings, list_ingredients)
            
            else:
                # save new ingquant and return list
                new_ingquant.ingredient = ingquant.ingredient
                list_ingredients[str(ing.ingredient)].remove(ing)
                list_ingredients[str(ing.ingredient)].append(new_ingquant)
                new_ingquant.save()
                return list_ingredients

    list_ingredients = {}
    user = request.user
    for shop in Shop.objects.filter(user = user):
        if shop.recipe:
            recipe = shop.recipe
            query = recipe.get_ingquants()
        else:
            shopping_list = shop.shopping_list
            query = shopping_list.get_ingquants()
        
        for ingquant in query:
            if str(ingquant.ingredient) in list_ingredients.keys():
                # for however many ingquants with the same ingredient
                copy = list_ingredients[str(ingquant.ingredient)].copy
                shopping_helper(ingquant, copy(), list_ingredients)
            else:
                list_ingredients[str(ingquant.ingredient)] = [ingquant]

    # take the list of ingredients and turn them into a dictionary of the form
    # category name: ingquants
    shopping = {}         
    for ingredient in list_ingredients.keys():
        category = list_ingredients[ingredient][0].ingredient.category
        if category in shopping.keys():
            for value in list_ingredients[ingredient]:
                shopping[category].append(value)
        else:
            if len(list_ingredients[ingredient]) == 1:
                shopping[category] = list_ingredients[ingredient]
            else:
                shopping[category] = [list_ingredients[ingredient][0]]
                additional_values = list_ingredients[ingredient].copy()
                additional_values.remove(list_ingredients[ingredient][0])
                for value in additional_values:
                    shopping[category].append(value)

    context = {
        "shopping": shopping, 
        'shopping_lists': query_shopping_lists(request),
        'user_id': request.user.id,
    }
    return context


@login_required
def shopping(request):
    context = get_shopping_context(request)
    return render(request, 'recipes/shopping.html', context)
    

@login_required
def update_ingredients(request):
    
    if request.method=='POST':
        data = json.loads(request.body)

        action = data.get('tag')
        requesting_user = request.user
        ingquant = IngQuant.objects.get(pk = data.get('ingquant_id'))
        
        if ingquant.recipe:
            recipe = ingquant.recipe
            model = Recipe
        elif ingquant.shopping_list:
            recipe = ingquant.shopping_list
            model = ShoppingList
            
        if model == Recipe:
            recipe = personalize_if_user_not_owner(requesting_user, recipe)

        # complete the requested action
        if action == 'rem' and recipe != -1:
            ctx = {
                "components": get_components(recipe),
                'unit_choices': UNIT_CHOICES,
                'category_choices': CATEGORY_CHOICES,
            }
            ingquant.delete()
            recipe.save()

    
        elif action =='edt':

            ingredient = ingquant.ingredient
            
            # check to see if it is already personalized
            if ingredient.ingredient[:3] != 'my ':
                # check to see if the personalized ingredient name is in the database
                if Ingredient.objects.filter(ingredient = 'my ' + ingredient.ingredient).count() != 0:
                    ingredient = Ingredient.objects.filter(ingredient = 'my ' + ingredient.ingredient)[0]
                else:
                    # create a new ingredient if not already personalized
                    ingredient = Ingredient(
                        ingredient = 'my ' + ingredient.ingredient,
                        user = request.user
                    )
                    ingredient.save()
                
            # update the ingredient
            if data.get('ing_category'): ingredient.category = CATEGORY_DICT[data.get('ing_category')]
            if data.get('serving_size'): ingredient.typical_serving_size = data.get('serving_size')
            if data.get('serving_unit'): ingredient.typical_serving_unit = data.get('serving_unit')
            if data.get('weight'): ingredient.weight_per_serving = data.get('weight')
            if data.get('calories'): ingredient.calories = data.get('calories')
            if data.get('fat'): ingredient.fat = data.get('fat')
            if data.get('transfat'): ingredient.transfats = data.get('transfat')
            if data.get('satfat'): ingredient.satfats = data.get('satfat')
            if data.get('polyunsatfat'): ingredient.polyunsatfats = data.get('polyunsatfat')
            if data.get('monounsatfat'): ingredient.monounsatfats = data.get('monounsatfat')
            if data.get('cholesterol'): ingredient.cholesterol = data.get('cholesterol')
            if data.get('sodium'): ingredient.sodium = data.get('sodium')
            if data.get('carbs'): ingredient.carbs = data.get('carbs')
            if data.get('fiber'): ingredient.fiber = data.get('fiber')
            if data.get('sugar'): ingredient.sugar = data.get('sugar')
            if data.get('protein'): ingredient.protein = data.get('protein')  
            ingredient.save()  

            # update the ingquant with the updated ingredient
            ingquant.ingredient = ingredient
            ingquant.save()
            
        ctx = {
            "components": get_components(recipe),
            'unit_choices': UNIT_CHOICES,
            'category_choices': CATEGORY_CHOICES,
        }
        return ajax(request, 'recipes/added_ingredients_list.html', ctx)
    
    return HttpResponse("POST request required")


def delete_recipe(request, recipe_id):
    return delete(request, Recipe, recipe_id, ingredient_id = None)


def delete_list(request, recipe_id):
    return delete(request, ShoppingList, recipe_id, ingredient_id = None)


def delete(request, model, recipe_id, ingredient_id = None):
    
    if model == ShoppingList:
        destination = "recipes:shopping" 
        error_destination = "recipes:update_shopping_list"
    else:
        destination = "recipes:index"
        error_destination = "recipes:display_edit_recipe"
    
    recipe = model.objects.get(pk = recipe_id)
    delete_object = recipe
    
    if ingredient_id != None:
        model = Ingredient
        destination = 'send to error dest'
        delete_object = model.objects.get(pk = ingredient_id)
    requesting_user = request.user

    if delete_object.user.id == requesting_user.id:
        delete_object.delete()
        if destination != 'send to error dest':
            return HttpResponseRedirect(reverse(destination))
        else:
            return HttpResponseRedirect(reverse(error_destination, args=(recipe_id,)))
    else:
        messages.info(request, 'You cannot delete something that does not belong to you.')
        return HttpResponseRedirect(reverse(error_destination, args=(recipe_id,)))


def cancel(request):
    valuenext = request.POST.get('next')
    return HttpResponseRedirect(valuenext)


def display_edit(request, object_id, model_name):
    ctx = {  
        'unit_choices': UNIT_CHOICES,
        'category_choices': CATEGORY_CHOICES,
        'model': model_name
    }
    
    if model_name == 'shopping_list':
        model = ShoppingList
    else:
        model = Recipe

    # called recipe, but could be shopping list also
    recipe = model.objects.get(pk = object_id)

    # recipe specific instructions
    if model == Recipe:
        # check to see if the user is the owner of the recipe
        if request.user == recipe.user:
            ctx['user_owner'] = True
        # if recipe not owned by user
        else:
            # check to see if there is a personalized recipe of the same name for that user
            recipe_alt = personalize_if_user_not_owner(request.user, recipe)
            # if personalize_if_user_not_owner changes the recipe, it is personalized
            if recipe_alt != -1:
                if recipe.id != recipe_alt.id:
                    ctx['already_personalized'] = True
                recipe = recipe_alt

        # get the steps of the recipe        
        steps = recipe.get_steps()
        if steps.count() > 0:
            ctx['steps'] = steps
            ctx['step_count'] = steps.count()

        ctx['meal_form'] = MealForm(initial={'type_of_meal': recipe.snack_or_meal.upper()}) 
        ctx['photo_form'] = RecipePhotoForm()

    # back to instructions for recipes and shopping lists
    ctx['recipe'] = recipe
    ctx['recipe_id'] = recipe.id
    ctx["components"] = get_components(recipe)

    ingredients = None

    if request.is_ajax():
        data = json.loads(request.body)
        url_parameter = data.get("q").strip()
        ctx["search"] = url_parameter

        if url_parameter == '':
            ctx['searched'] = False
        elif url_parameter:
            ctx['searched'] = True
            url_parameters = url_parameter.split()
            args = []
            for param in url_parameters:
                param = param.strip(", /-")
                args.append(Q(ingredient__icontains=param))
            # need to only return ingredients that are public or belong to the user
            ingredients = Ingredient.objects.filter(*args).filter(Q(user = None) | Q(user = request.user))
            if ingredients.count() > 0:
                ctx["ingredients"] = ingredients
            else:
                ctx['searched'] = True

        return ajax(request, 'recipes/ingredient_list.html', ctx)

    if model == Recipe:
        return render(request, 'recipes/edit_recipe.html', context = ctx)
    else:
        return render(request, 'recipes/edit_shopping_list.html', context = ctx)


def record_edit(request, object_id, model):
    recipe = model.objects.get(pk = object_id)
    requesting_user = request.user
    
    if model == ShoppingList:
        destination = "recipes:update_shopping_list"
    # just recipes
    else: 
        destination = "recipes:display_edit_recipe"
        recipe = personalize_if_user_not_owner(requesting_user, recipe)
        # if there is an error and the recipe shows up more than once in the database
        if recipe == -1:
            messages.error(request, "The recipe already exists in the database. Please edit  it from its own page.")
            return HttpResponseRedirect(reverse(destination, args=(recipe.id,))) 
        recipe.prep_time = request.POST.get('prep')
        recipe.cook_time = request.POST.get('cook')
        recipe.servings = request.POST.get('servings')
        recipe.notes = request.POST.get('notes')
        recipe.author = request.POST.get('author')
        if request.POST.get('public') != None: 
            recipe.public = True
        else:
            recipe.public = False

        meal_form = MealForm(request.POST)
        if meal_form.is_valid():
            recipe.snack_or_meal = meal_form.cleaned_data.get('type_of_meal')

        photo_form = RecipePhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            if photo_form.cleaned_data.get('photo') != None:
                recipe.photo = photo_form.cleaned_data.get('photo')
        
        # record steps
        num_steps = int(request.POST.get("num_steps"))
        if num_steps > 0:
            # delete previously created steps 
            recipe.get_steps().delete()

        # add in new steps
        count = 0
        for i in range(num_steps + 1):
            step = request.POST.get("step_" + str(i))
            if step != "" and step != None:
                step = step.strip()
                step = Step(
                    step = step,
                    order = count, 
                    recipe = recipe
                )
                count += 1
                step.save()

    # recipe and shopping list
    recipe.name = normalize(request.POST.get('name'))
    recipe.description = request.POST.get('description')
    recipe.user = request.user

    added_components = recipe.get_ingquants()
    components_ingredients = []
    for component in added_components:
        components_ingredients.append(component.ingredient.id)
        new_quantity = request.POST.get('quantity_' + str(component.id), None)
        if new_quantity != None:
            component.quantity = new_quantity
        new_unit = request.POST.get('name_' + str(component.id) +"-choose_unit", None)
        if new_unit != None:
            component.unit = new_unit
        component.save()

    recipe.save()
    
    if model == Recipe:
        model_name = 'recipe'
    else:
        model_name = 'shopping_list'

    # if request.POST.get('add_ingredient') != None:
    #     return add_ingredient(request, source = model_name)
    
    # if request.POST.get('save_ingredient') != None:
    #     ingredient_id = request.POST.get('save_ingredient')[16:]
    #     return add_ingredient(request, ingredient_id, source = model_name)
    
    # if request.POST.get('delete_ingredient') != None:
    #     ingredient_id = request.POST.get('delete_ingredient')[18:]
    #     return delete(request, model, recipe.id, ingredient_id)
 
    if model == Recipe:
        return HttpResponseRedirect(reverse("recipes:detail", args=(recipe.id,)))
    else:
        return HttpResponseRedirect(reverse("recipes:detail_shopping_list", args=(recipe.id,)))


def delete_ing(request, recipe_id):
    data = json.loads(request.body)
    ingredient = Ingredient.objects.get(pk = data.get('ing_id'))
    ingredient.delete()

    model = data.get('model')
    if model == 'recipe':
        model = Recipe
    elif model == 'shopping_list':
        model = ShoppingList

    recipe = model.objects.get(pk = recipe_id)

    return ajax(request, 'recipes/added_ingredients_list.html', {'components': get_components(recipe)})


def add_ing_to_list(request, recipe_id):
    data = json.loads(request.body)

    if data.get('model') == 'recipe':
        model = Recipe
    elif data.get('model') == 'shopping_list':
        model = ShoppingList

    recipe = model.objects.get(pk = recipe_id)
    if model == Recipe:
        ingquants = IngQuant.objects.filter(recipe = recipe)
    elif model == ShoppingList:
        ingquants = IngQuant.objects.filter(shopping_list = recipe)

    components = []
    for ingquant in ingquants:
        components.append(ingquant.ingredient)
    
    added_ingredient = Ingredient.objects.get(pk = data.get('ingredient_id'))
    if added_ingredient not in components:
        if model == Recipe:
            ing = IngQuant(
                ingredient = added_ingredient,
                recipe = recipe
            )
        elif model == ShoppingList:
            ing = IngQuant(
                ingredient = added_ingredient,
                shopping_list = recipe
            )
        ing.save()
        components.append(ing)
    # already added to ingredients list
    else:
        messages.info(request, f"'{added_ingredient.ingredient[0].upper()}{added_ingredient.ingredient[1:]}' is already in the ingredients list.")
    
    return ajax(request, 'recipes/added_ingredients_list.html', {'components': get_components(recipe)})


def update_shopping_list(request, recipe_id):
    return display_edit(request, recipe_id, 'shopping_list')


def record_shopping_list(request, recipe_id):
    return record_edit(request, recipe_id, ShoppingList)


def detail_shopping_list(request, recipe_id):
    if request.method == "POST":
        return HttpResponseRedirect(reverse("recipes:detail_shopping_list", kwargs= {"recipe_id": recipe_id,}))
    else:
        shopping_list = get_object_or_404(ShoppingList, pk = recipe_id)

        ingquants = shopping_list.get_ingquants()
        ingquantsAndUnits = []
        for ingquant in ingquants:
            unit = ingquant.unitDisplay()
            ingquantsAndUnits.append((ingquant, unit))

        ctx = {
            'recipe': shopping_list,
            'ingredients': ingquantsAndUnits,
            'shopping_list': [shopping_list]
        }

        return render(request, 'recipes/detail_shopping_list.html', ctx)


def index_shopping_lists(request):
    return index(request, model_name = 'shopping_list')


def get_plan_objects(request):
    elements = Plan.objects.filter(user = request.user)
    recipes = []
    ingredients = []
    for element in elements:
        try:
            if element.recipe != None:
                recipes.append(element.recipe)
        except:
            try:
                if element.ingredient != None:
                    ingredients.append(element.ingredient)
            except:
                messages.info(request, 'Something went wrong with loading your planned recipes.')
                return -1
    
    return (recipes, ingredients)


@login_required
def planning(request):
    plans = MealPlan.objects.filter(user = request.user)

    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    today = datetime.today()
    active_plans = MealPlan.objects.filter(start_date__lte=today, end_date__gte=today)
    if active_plans:
        current_plan = active_plans[0]
    else:
        try:
            current_plan = MealPlan.objects.latest('id')
        except MealPlan.DoesNotExist:
            current_plan = None

    ctx = {}
    if current_plan:
        days = range(current_plan.days)
        ctx = get_display_edit_plan_ctx(request, current_plan.id)
    ctx.update({
        'current_plan': current_plan,
        'display_only': True,
        'page_obj': page_obj,
    })
    return render(request, 'recipes/mealplanning.html', context = ctx)


@login_required
def create_plan(request):

    plan_number = MealPlan.objects.filter(user = request.user).count() + 1  
    
    ctx = {
        'plan_number': plan_number,
        'meal_time_choices': MEALTIME_CHOICES,
        'today': datetime.now().strftime('%Y-%m-%d')
    }
        
    if request.method == 'POST':
        
        name = request.POST.get('name') 
        people = request.POST.get('people')
        start_date = request.POST.get('startdate')
        end_date = request.POST.get('enddate')
        days = request.POST.get('days')
        notes = request.POST.get('notes')
        breakfast = request.POST.get('breakfast')
        lunch = request.POST.get('lunch')
        dinner = request.POST.get('dinner')
        snack = request.POST.get('snack')
        dessert = request.POST.get('dessert') 
        other = request.POST.get('other')

        # Check to make sure name is unique
        if MealPlan.objects.filter(name = name, user = request.user).count() > 0:
            messages.info(request, ("You already have a plan called " + name + ". Please use a unique name."))
            ctx['plan'] = MealPlan.objects.filter(name = name, user = request.user)[0]
            return render(request, 'recipes/create_plan.html', ctx) 
        
        # Check to make sure number of days is > 0
        if int(days) <= 0:
            messages.info(request, ("Please enter a positive number of days."))
            return render(request, 'recipes/create_plan.html', ctx) 
        
        # Check to make sure dates and number of days match
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        calculated_days = (end_date - start_date).days + 1
        if calculated_days != int(days):
            messages.info(request, ("Calculated number of days does not match number of days entered."))
            return render(request, 'recipes/create_plan.html', ctx) 

        # Check to make sure number of people is > 0
        if int(people) <= 0:
            messages.info(request, ("Please enter a positive number of people."))
            return render(request, 'recipes/create_plan.html', ctx) 

        meals = {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'snack': snack,
            'dessert': dessert,
            'other': other,
        }
        # record which meals will be planned
        for key in meals.keys():
            if meals[key] == None:
                meals[key] = False
            else:
                meals[key] = True


        new_plan = MealPlan(
            name = name,
            user = request.user,
            notes = notes,
            start_date = start_date,
            end_date = end_date,
            days = days, 
            people = people,
            breakfast = meals['breakfast'],
            lunch = meals['lunch'], 
            dinner = meals['dinner'], 
            snack = meals['snack'], 
            dessert = meals['dessert'], 
            other = meals['other'],
        )
        new_plan.save()

        # create and save all the new planned meals
        meals = get_plan_meals(new_plan)[0]
        for day in range(int(days)):
            for meal in meals:
                planned_meal = PlannedMeal(
                    meal = meal,
                    day = day,
                    meal_plan = new_plan,
                    user = request.user,
                    servings = people
                )
                planned_meal.save()

        return HttpResponseRedirect(reverse("recipes:display_edit_plan", kwargs= {"plan_id": new_plan.id,}))
        
    return render(request, 'recipes/create_plan.html', context = ctx)


def get_plan_meals(plan):
    meal_attribs = {
        'breakfast': plan.breakfast,
        'brunch': plan.brunch,
        'lunch': plan.lunch,
        'dinner': plan.dinner,
        'snack': plan.snack,
        'dessert': plan.dessert,
        'other': plan.other,
    }

    # get a list of the meals for the plan
    meals = []
    add_meals = []
    for key in meal_attribs.keys():
        if meal_attribs[key]:
            meals.append(key)
        else: 
            add_meals.append(key)
    
    return (meals, add_meals)


def get_display_edit_plan_ctx(request, plan_id):
    # get the plan itself
    plan = MealPlan.objects.get(pk = plan_id)

    # get a dictionary of planned meals with a key of the day
    # int for day: [list of planned meals for that day])
    planned_meals = {}
    days = []
    for i in range(plan.days):
        planned_meals[i] = []
        for meal in MEALTIME_CHOICES:
            this_meal = PlannedMeal.objects.filter(
                meal_plan = plan, 
                day = i, 
                user=request.user,
                meal = meal[1]
                )
            if this_meal:
                planned_meals[i].append(this_meal[0])

        meals_planned = []
        add_meals = []
        for meal in MEALTIME_CHOICES:
            if PlannedMeal.objects.filter(meal_plan = plan, day = i, user=request.user, meal = meal[1]):
                meals_planned.append(meal[1])
            else:
                add_meals.append(meal[1])
        days.append((int(i), meals_planned, add_meals))
    
    planned = get_plan_meals(plan)
    meals = planned[0]
    # add_meals = planned[1]

    ctx = {
        'plan': plan, 
        'meals': meals,
        'meal_time_choices': MEALTIME_CHOICES,
        # 'add_meals': add_meals,
        'planned_meals': planned_meals,
        'days': days
    }

    # get the recipes and ingredients lined up for the plan
    objects = get_plan_objects(request)
    if objects != -1:
        ctx['recipes'] = objects[0]
        ctx['ingredients'] = objects[1]

    return ctx


def plan_add_recipe(request, plan_id):
    plan = MealPlan.objects.get(pk = plan_id)
    data = json.loads(request.body)
    recipe_id = data.get("recipe_id").strip()
    recipe = Recipe.objects.get(pk = recipe_id)
    if recipe == None:
        return JsonResponse({'messages': 'Recipe not found.'})

    day = data.get("day").strip()
    if day == 'all':
        planned_meals = []
        pre_planned_meals = data.get('planned_meals')
        for ppm in pre_planned_meals:
            temp = Recipe.objects.get(pk = ppm)
            planned_meals.append(temp)
        
        if data.get('add_or_remove') == 'add':
            planned_meals.append(recipe)
        else:
            planned_meals.remove(recipe)

        return ajax(request, 'recipes/plan_added_recipes.html', {
            'recipes': planned_meals,
            'day': 'all',
        })

    else:
        day = int(data.get("day").strip())   
        meal = data.get("meal").strip().lower()

        # try to get a planned meal
        try: 
            planned_meal = PlannedMeal.objects.get(user = request.user, meal_plan = plan, meal = meal, day = day)

        except PlannedMeal.DoesNotExist:
            print('creating new plan - caution - this should not happen')
            # add a new meal if one does not exist yet
            planned_meal = PlannedMeal(
                user = request.user,
                meal_plan = plan,
                meal = meal,
                day = day,
            )
            planned_meal.save()

        if data.get('add_or_remove') == 'add':
            # add the selected food to the planned meal
            planned_meal.recipes.add(recipe)
        else:
            # remove the selected recipe
            planned_meal.recipes.remove(recipe)

        # return html
        return ajax(request, 'recipes/plan_added_recipes.html', {
            'recipes': planned_meal.recipes.all(),
            'day': day,
            'meal': meal
        })


def list_recipes(request, plan_id):

    plan = MealPlan.objects.get(pk = plan_id)
    data = json.loads(request.body)
    q = data.get("q").strip()

    qs = q.split()
    args = []
    for param in qs:
        param = param.strip(", /-")
        args.append(Q(name__icontains=param))
    # need to only return recipes that are public or belong to the user
    recipes = Recipe.objects.filter(*args).filter(Q(public = True) | Q(user = request.user))

    return ajax(request, 'recipes/recipe_list.html', {'recipes': recipes})


@login_required
def display_edit_plan(request, plan_id):
    
    ctx = get_display_edit_plan_ctx(request, plan_id)

    return render(request, 'recipes/edit_meal_plan.html', context = ctx)


@login_required
def record_planned_meal(request):

    # get the plan itself
    plan_id = request.POST.get('plan_id')
    plan = MealPlan.objects.get(pk = plan_id)

    # and the info we already have about the planned meal
    user = request.user
    day = request.POST.get('day')
    meal = request.POST.get('meal')
    
    meal_id = request.POST.get('meal_id')
    if meal_id:
        planned_meal = PlannedMeal.objects.get(pk = meal_id)
    else:
        # create a new planned meal
        planned_meal = PlannedMeal(
            meal = meal,
            day = day,
            meal_plan = plan,
            user = user,
        )
    planned_meal.save()

    # info to be recorded
    food_type = request.POST.get('food_type')
    food_id = request.POST.get('food_id')
    servings = request.POST.get('servings')

    if food_type != None and food_id != None:
        if food_type == 'rec':
            recipe = Recipe.objects.get(pk = food_id)
            planned_meal.recipes.add(recipe)
        elif food_type == 'ing':
            ing = Ingredient.objects.get(pk = food_id)
            planned_meal.ingredients.add(ing)
        else:
            message.info(request, 'Error recording food addition to a meal.')

    if servings != None:
        planned_meal.servings = servings
    
    planned_meal.save()

    ctx = get_display_edit_plan_ctx(request, plan_id)
    ctx['day'] = int(planned_meal.day)
    
    return ajax(request, 'recipes/meal_plan_card.html', ctx)


@login_required
def index_plans(request):
    plans = MealPlan.objects.filter(user = request.user)
    return render(request, 'recipes/plan_index.html', {'plans': plans})


def save_plan(request, plan_id):
    plan = MealPlan.objects.get(pk = plan_id)
     
    # get all the planned meals that are associated with this plan
    planned_meals = plan.planned_meals.all()

    # for each meal
    for pm in planned_meals:
        day = str(pm.day).rjust(3, '0')
        meal = pm.meal
        # record the number of servings per meal
        servings = request.POST.get('meal_servings_' + day + '_' + meal)
        if servings:
            pm.servings = servings
        # record any notes
        notes = request.POST.get('notes_' + day + '_' + meal)
        if notes:
            pm.notes = notes
        pm.save()

    # record the notes about this plan
    notes = request.POST.get('notes')
    if notes:
        plan.notes = notes

    # record the number of people
    people = request.POST.get('people')
    if people:
        plan.people = people
    
    plan.save()
    return 


def update_and_edit_plan(request, plan_id):
    save_plan(request, plan_id)

    return HttpResponseRedirect(reverse("recipes:display_edit_plan", kwargs= {"plan_id": plan_id,}))


@login_required
def update_plan(request, plan_id):
    
    save_plan(request, plan_id)

    return HttpResponseRedirect(reverse("recipes:plan_detail", kwargs= {"plan_id": plan_id,}))


def update_plan_ajax(request, plan_id):
    data = json.loads(request.body)
    plan = MealPlan.objects.get(pk = plan_id)

    day = data.get('day')
    meal = data.get('meal')

    if data.get('add_meal') and PlannedMeal.objects.filter(
            meal = meal,
            day = day,
            meal_plan = plan,
            user = request.user
        ).count() == 0:
        planned_meal = PlannedMeal(
                meal = meal,
                day = day,
                meal_plan = plan,
                user = request.user,
                servings = plan.people
            )
        planned_meal.save()

    elif data.get('remove_meal'):
        if data.get('meal') == 'day':
            # delete all the meals for that day
            meals_of_the_day = PlannedMeal.objects.filter(
                day = day,
                meal_plan = plan,
                user = request.user
            )
            if meals_of_the_day:
                for meal in meals_of_the_day:
                    meal.delete()

            # below is code to update the number of days in the plan. 
            # However, I chose to keep the plan as is in case a user wants to just 
            # skip planning something for that day but not adjust the whole plan.
            # update the meal plan's info       
            # plan.days = plan.days - 1
            # end_date = plan.end_date + timedelta(days = -1)
            # plan.save()

        else:
            planned_meal = PlannedMeal.objects.get(
                meal = meal,
                day = day,
                meal_plan = plan,
                user = request.user,
            )
            planned_meal.delete()

    meals_planned = []
    add_meals = []
    for meal in MEALTIME_CHOICES:
        if PlannedMeal.objects.filter(meal_plan = plan, day = day, user=request.user, meal = meal[1]):
            meals_planned.append(meal[1])
        else:
            add_meals.append(meal[1])

    ctx = get_display_edit_plan_ctx(request, plan.id)
    ctx['day'] = (int(day), meals_planned, add_meals)
    return ajax(request, 'recipes/meal_plan_card.html', ctx)


def add_base_meals(request, plan_id):
    data = json.loads(request.body)
    plan = MealPlan.objects.get(pk = plan_id)
    meal = data.get('meal')
    add = data.get('add')

    # update the plan as a whole
    if meal == 'breakfast': plan.breakfast = add
    if meal == 'brunch': plan.brunch = add
    if meal == 'lunch': plan.lunch = add
    if meal == 'dinner': plan.dinner = add
    if meal == 'snack': plan.snack = add
    if meal == 'dessert': plan.dessert = add
    if meal == 'other': plan.other = add
    plan.save()

    # update each planned meal
    for day in range(plan.days):

        planned_meal = PlannedMeal.objects.filter(
                meal = meal,
                day = day,
                meal_plan = plan,
                user = request.user
            )

        if add == True and planned_meal.count() == 0:
            # add the meal to every day that doesn't already have it
            new_meal = PlannedMeal(
                meal = meal,
                day = day,
                meal_plan = plan,
                user = request.user,
                servings = plan.people
            )
            new_meal.save()

        elif add == False and planned_meal.count() == 1:
            # remove any of the named meal that doesn't alreay have data
            planned_meal = PlannedMeal.objects.get(
                    meal = meal,
                    day = day,
                    meal_plan = plan,
                    user = request.user,
                )
            if planned_meal.recipes.all() or planned_meal.ingredients.all() or planned_meal.notes:
                pass
            else:
                planned_meal.delete()             

    ctx = get_display_edit_plan_ctx(request, plan.id)

    return ajax(request, 'recipes/plan_days.html', ctx)


def update_days(request, plan_id):
    data = json.loads(request.body)
    plan = MealPlan.objects.get(pk = plan_id)

    startdate = datetime.strptime(data.get('startdate'), '%Y-%m-%d').date() 
    enddate = datetime.strptime(data.get('enddate'), '%Y-%m-%d').date() 

    meals = {
        'breakfast': plan.breakfast,
        'brunch': plan.brunch,
        'lunch': plan.lunch,
        'dinner': plan.dinner,
        'snack': plan.snack,
        'dessert': plan.dessert,
        'other': plan.other
    }
    
    # add new days at the beginning, with appropriate meals, changing all future planned meals to day + delta

    # find out how many days to add to beginning
    start_delta = (plan.start_date - startdate).days
    # days to add to end
    end_delta = (enddate - plan.end_date).days

    if start_delta != 0:
        # for all planned meals, adjust day in plan
        existing_meals = PlannedMeal.objects.filter(
                    meal_plan = plan, 
                    user = request.user
                )
        for existing_meal in existing_meals:
            existing_meal.day = existing_meal.day + start_delta
            existing_meal.save()
    
    if start_delta < 0 or end_delta < 0:
        delta = max(abs(start_delta), abs(end_delta))
        for day in range(abs(delta)):
            new_day = day - 1
            if end_delta < 0:
                new_day = plan.days - day - 1
            PlannedMeal.objects.filter(
                meal_plan = plan, 
                day = new_day,
                user = request.user
            ).delete()
    elif start_delta > 0 or end_delta > 0:
        delta = max(start_delta, end_delta)
        for day in range(delta):
            new_day = day
            if end_delta > 0:
                new_day = day + plan.days
            for key in meals.keys():
                if meals[key] and PlannedMeal.objects.filter(
                        meal_plan = plan, 
                        meal = key,
                        day = new_day,
                        user = request.user
                    ).count() == 0:
                    new_meal = PlannedMeal(
                        meal_plan = plan, 
                        meal = key,
                        day = new_day,
                        user = request.user
                    )
                    new_meal.save()

    # adjust plan's number of days and startdate
    plan.start_date = startdate
    plan.end_date = enddate
    plan.days = (plan.end_date - plan.start_date).days + 1
    plan.save()

    ctx = get_display_edit_plan_ctx(request, plan.id)

    return ajax(request, 'recipes/plan_days.html', ctx) 


def plan_detail(request, plan_id):
    
    ctx = get_display_edit_plan_ctx(request, plan_id)
    ctx['display_only'] = True

    return render(request, 'recipes/plan_display.html', context = ctx)


def bulk_add(request, plan_id):

    data = json.loads(request.body)
    plan = MealPlan.objects.get(pk = plan_id)

    planned_recipes = data.get('planned_meals')
    frequency = data.get('frequency')
    meal = data.get('meal')

    if frequency == 'empty':
        for day in range(plan.days):
            try:
                planned_meal = PlannedMeal.objects.get(
                    user = request.user,
                    meal_plan = plan,
                    meal = meal,
                    day = day
                )
                print(planned_meal.recipes.all())
                if not planned_meal.recipes.all():
                    for pr in planned_recipes:
                        planned_meal.recipes.add(
                            Recipe.objects.get(pk = pr)
                        )
                        planned_meal.save()
            except PlannedMeal.DoesNotExist:
                print('meal does not exist', day, meal)
    else:
        # default is to add a recipe to every day
        set_range = range(plan.days)
        if frequency == 'every_even':
            set_range = range(1, plan.days + 1, 2)
        elif frequency == 'every_odd':
            set_range = range(0, plan.days + 1, 2)

        for day in set_range:
            try:
                planned_meal = PlannedMeal.objects.get(
                    user = request.user,
                    meal_plan = plan,
                    meal = meal,
                    day = day
                )
                for pr in planned_recipes:
                    planned_meal.recipes.add(
                        Recipe.objects.get(pk = pr)
                    )
                    planned_meal.save()
            except PlannedMeal.DoesNotExist:
                print('meal does not exist', day, meal)
     

    ctx = get_display_edit_plan_ctx(request, plan.id)
    return ajax(request, 'recipes/plan_days.html', ctx) 


def delete_plan(request, plan_id):
    plan = MealPlan.objects.get(pk = plan_id)
    if plan:
        if plan.user == request.user:
            plan.delete()
        else:
            next_pg = request.GET.get('next')
            messages.info(request, 'You cannot delete something that does not belong to you.')
    else:
        messages.info(request, 'Plan no longer exists')
    return HttpResponseRedirect(reverse("recipes:planning"))    