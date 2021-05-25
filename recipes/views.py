from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


from .models import Recipe, Ingredient, IngQuant, Step, Favorites, Shop, Plan, ShoppingList
from .models import VOLUME, WEIGHT, UNIT, UNIT_CHOICES, MEAL_CHOICES, CATEGORY_CHOICES, UNIT_DICT, CATEGORY_DICT
from .convert_units import convert_units, get_smaller_unit
from .forms import MealForm, UnitForm, CategoryForm, RecipePhotoForm

# Utility functions

def normalize(data):
    return data.strip().lower()


# Page views

def index(request, model_name='recipe'):
    
    if model_name == "shopping_list":
        model = ShoppingList
    else:
        model = Recipe

    if not request.user.is_authenticated:
        recipe_list = model.objects.filter(public = True).order_by('-name')
    else:
        user = request.user
        # basic list already has 'mine' filter
        recipe_list = model.objects.filter(user=user).order_by('-name')
        print(recipe_list)  
        filter = request.GET.get('radio')
        filter_status = request.GET.get('status')
        print('filter status', filter, filter_status)
        if filter != None and filter_status == 'true':
            if filter == 'all':
                recipe_list = model.objects.filter(Q(user = user) | Q(public = True)).order_by('-name')
            elif filter == 'public':
                recipe_list = model.objects.filter(public = True).order_by('-name')
            elif filter == 'favorites':
                favorites = Favorites.objects.filter(user = user)
                pks = []
                for favorite in favorites:
                    pks.append(favorite.recipe.id)
                recipe_list = model.objects.filter(pk__in = pks)
    if request.GET.get("q") != None:
        recipe_list = recipe_list.filter(name__icontains=request.GET.get("q").lower())

    ctx = {
        'request': request, 
    }
    
    if model == ShoppingList:
        ctx['shopping_lists'] = query_shopping_lists(request)
    else:
        ctx['recipe_list'] = recipe_list

    if request.is_ajax():
        return ajax(request, 'recipes/index_cards.html', ctx)

    return render(request, "recipes/index.html", ctx) 

def index_all(request):
    if request.user.is_authenticated:
        user = request.user
        recipe_list = Recipe.objects.filter(Q(public = True) | Q(user = user)).order_by('-name')
    else: 
        recipe_list = Recipe.objects.filter(public = True).order_by('-name')
    return render(request, "recipes/index.html", {'recipe_list': recipe_list, 'request': request}) 


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
def create_recipe(request):
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
        return render(request, 'recipes/create_recipe.html')


def get_components(recipe):
    components = []
    ingquants = recipe.get_ingquants()
    for ingquant in ingquants:
        form = UnitForm(initial={'choose_unit': ingquant.unit.upper()}, prefix="name_" + str(ingquant.id))
        components.append((ingquant, form))
    return components


@login_required
def display_edit_recipe(request, recipe_id):
    return display_edit(request, recipe_id, 'recipe')

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
        ing.recipe = recipe
        
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

@login_required
def planning(request):
    return HttpResponse("TODO")


@login_required
def button_ajax(request):
    data = {'success': False} 
    if request.method=='POST':
        model = request.POST.get('model')
        if model == 'shopping_list':
            model_update = ShoppingList
        else:
            model_update = Recipe
        recipe_id = request.POST.get('recipe_id')
        recipe = model_update.objects.get(pk = recipe_id)
        action = request.POST.get('tag')
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
            data['success'] = True
            data['action'] = "add"
        else:
            inst = match[0]
            inst.delete()
            data['success'] = True
            data['action'] = "remove"
        
        source = request.POST.get('source')
        if source == 'shopping':
            template = loader.get_template('recipes/current_shopping_list.html')
            context = get_shopping_context(request)
            html = template.render(context, request)
            print(html)
            data["html_from_view"] = html
            return JsonResponse(data=data, safe=False)
        else:
            return JsonResponse(data)
    else: 
        return HttpResponse("Something went wrong recording your button click on " + action)

@login_required
def update_ingredients(request):
    data = {'success': False} 
    
    if request.method=='POST':
        action = request.POST.get('tag')
        requesting_user = User.objects.get(pk=int(request.POST.get('user_id')))
        ingquant = IngQuant.objects.get(pk = request.POST.get('ingquant_id'))
        recipe = ingquant.recipe
    
        personalize_if_user_not_owner(requesting_user, recipe)

        # complete the requested action
        if action == 'rem':
            ctx = {}
            ingquant.delete()
            recipe.save()
            
            ctx["components"] = get_components(recipe)
            template = loader.get_template('recipes/added_ingredients_list.html')
            context = ctx
            html = template.render(context, request)
            data = {
                "html_from_view": html, 
                'success': True,
            }
            return JsonResponse(data=data, safe=False)
    
    return HttpResponse("Something went wrong with updating ingredients.")

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
    print('model, dest, error dest', model, destination, error_destination)
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
        'user_id': request.user.id,
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
    searched = False
    url_parameter = request.GET.get("q")
    ctx["search"] = url_parameter
    if url_parameter:
        url_parameters = url_parameter.split()
        args = []
        for param in url_parameters:
            param = param.strip(", /-")
            args.append(Q(ingredient__icontains=param))
        # need to only return ingredients that are public or belong to the user
        ingredients = Ingredient.objects.filter(*args).filter(Q(user = None) | Q(user = request.user))
        ctx["ingredients"] = ingredients

    if request.is_ajax():
        return ajax(request, 'recipes/ingredient_list.html', ctx)

    if model == Recipe:
        return render(request, 'recipes/edit_recipe.html', context = ctx)
    else:
        return render(request, 'recipes/edit_shopping_list.html', context = ctx)

def ajax(request, template, ctx):
    ctx['searched'] = True
    template = loader.get_template(template)
    context = ctx
    html = template.render(context, request)
    data_dict = {
        "html_from_view": html, 
    }
    return JsonResponse(data=data_dict, safe=False)

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

    print('requests', request.POST.get('add_to_recipe'), request.POST.get('add_ingredient'), request.POST.get('save_ingredient'), request.POST.get('delete_ingredient'))
    if request.POST.get('add_to_recipe') != None:
        added_ingredient = Ingredient.objects.filter(ingredient = request.POST['ingredient_name'])
        if added_ingredient[0].id not in components_ingredients:
            ing = IngQuant(
                ingredient = added_ingredient[0],
            )
            if model == Recipe:
                ing.recipe = recipe
            else:
                ing.shopping_list = recipe
            ing.save()
        # already added to ingredients list
        else:
            messages.info(request, added_ingredient[0].ingredient + " is already in the ingredients list.")
        return HttpResponseRedirect(reverse(destination, args=(recipe.id,)))
    
    if model == Recipe:
        model_name = 'recipe'
    else:
        model_name = 'shopping_list'

    if request.POST.get('add_ingredient') != None:
        return add_ingredient(request, source = model_name)
    
    if request.POST.get('save_ingredient') != None:
        ingredient_id = request.POST.get('save_ingredient')[16:]
        return add_ingredient(request, ingredient_id, source = model_name)
    
    if request.POST.get('delete_ingredient') != None:
        ingredient_id = request.POST.get('delete_ingredient')[18:]
        return delete(request, model, recipe.id, ingredient_id)
 
    if model == Recipe:
        return HttpResponseRedirect(reverse("recipes:detail", args=(recipe.id,)))
    else:
        return HttpResponseRedirect(reverse("recipes:detail_shopping_list", args=(recipe.id,)))

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