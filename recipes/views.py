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


from .models import Recipe, Ingredient, IngQuant, Step, Favorites, Shop, Plan
from .models import VOLUME, WEIGHT, UNIT, UNIT_CHOICES, MEAL_CHOICES, CATEGORY_CHOICES
from .convert_units import convert_units, get_smaller_unit
from .forms import MealForm, UnitForm, CategoryForm, RecipePhotoForm


def normalize(data):
    return data.strip().lower()

def index(request):
    if request.user.is_authenticated:
        # TODO AJAX search
        if request.GET.get("q") == None:
            user = request.user
            recipe_list = Recipe.objects.filter(user=user).order_by('-name')
        else:
            recipe_list = Recipe.objects.filter(name__icontains=request.GET.get("q"), user=user)
    else:
        recipe_list = Recipe.objects.filter(public = True).order_by('-name')

    return render(request, "recipes/index.html", {'recipe_list': recipe_list, 'request': request}) 

def index_all(request):
    if request.user.is_authenticated:
        user = request.user
        recipe_list = Recipe.objects.filter(Q(public = True) | Q(user = user)).order_by('-name')
    else: 
        recipe_list = Recipe.objects.filter(public = True).order_by('-name')
    return render(request, "recipes/index.html", {'recipe_list': recipe_list, 'request': request}) 

@login_required
def detail(request, recipe_id):
    if request.method == "POST":
        return HttpResponseRedirect(reverse("recipes:detail", kwargs= {"recipe_id": recipe_id,}))
    else:
        recipe = get_object_or_404(Recipe, pk = recipe_id)

        ingquants = recipe.get_ingquants()
        ingquantsAndUnits = []
        for ingquant in ingquants:
            unit = ingquant.unitDisplay()
            ingquantsAndUnits.append((ingquant, unit))


        # TODO: make nutrition reflect actual recipe
        nutrition = {
            'calories': 100,
            'fat': 5,
            'satfat': 3
        }
        uncounted = (
            'cookies',
            'cakes'
        )
        # If an ingredient belongs to a user, add a note that the nutrition information is not verified

        ctx = {
            'recipe': recipe,
            'steps': recipe.get_steps(),
            'ingredients': ingquantsAndUnits,
            'total': recipe.get_total_time(),
            'nutrition': nutrition,
            'uncounted': uncounted
        }

        return render(request, 'recipes/detail.html', ctx)

@login_required
def create_recipe(request):
    if request.method == "POST":
        new_recipe = request.POST.get("recipe_name")
        if new_recipe != None:
            new_recipe = new_recipe.lower().strip()
            
            # Check to make sure name is unique
            if Recipe.objects.filter(name = new_recipe, user = request.user).count() > 0:
                ctx = {
                    "error_message": "You already have a recipe called " + new_recipe + ". Please use a unique name ",
                    "recipe": Recipe.objects.filter(name = new_recipe, user = request.user)[0]
                }
                return render(request, 'recipes/create_recipe.html', ctx) 
                
            # if unique, create new recipe    
            else:
                add_recipe = Recipe()
                add_recipe.name = new_recipe
                add_recipe.user = request.user
                add_recipe.save()
                
        return HttpResponseRedirect(reverse("recipes:display_edit_recipe", kwargs= { "recipe_id": add_recipe.id, }))
    else:
        return render(request, 'recipes/create_recipe.html', context = {})


def get_components(recipe):
    components = []
    ingquants = recipe.get_ingquants()
    for ingquant in ingquants:
        form = UnitForm(initial={'choose_unit': ingquant.unit.upper()}, prefix="name_" + str(ingquant.id))
        components.append((ingquant, form))
    return components


@login_required
def display_edit_recipe(request, recipe_id):
    
    ctx = {  
        "photo_form": RecipePhotoForm(),
        'user_id': request.user.id,
        'new_ing_unit_form': UnitForm(),
        'category_form': CategoryForm(),
    }

    recipe_init = Recipe.objects.get(pk = recipe_id)
    recipe_init_id = recipe_init.id
    # check to see if there is a personalized recipe of the same name for that user
    recipe = personalize_if_user_not_owner(request.user, recipe_init)
    # if personalized_if_user_not_owner changes the recipe, it is personalized
    if recipe.id != recipe_init_id:
        ctx['already_personalized'] = True

    ctx['recipe'] = recipe
    ctx['meal_form'] = MealForm(initial={'type_of_meal': recipe.snack_or_meal.upper()})
    ctx['recipe_id'] = recipe.id

    if request.user == recipe.user:
        ctx['user_owner'] = True

    ctx["components"] = get_components(recipe)

    steps = recipe.get_steps()
    if steps.count() > 0:
        ctx['steps'] = steps
        ctx['step_count'] = steps.count()
    
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
        searched = True
        if ctx['ingredients'].count() == 0:
            # get ready to create a new ingredient
            ctx['searched'] = searched
            template = loader.get_template('recipes/ingredient_list.html')
            context = ctx
            html = template.render(context, request)
        else:
            ctx['searched'] = searched
            template = loader.get_template('recipes/ingredient_list.html')
            context = ctx
            html = template.render(context, request)
        data_dict = {
            "html_from_view": html, 
        }
        return JsonResponse(data=data_dict, safe=False)

    return render(request, 'recipes/edit_recipe.html', context = ctx)

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
    recipe = Recipe.objects.get(pk = recipe_id)
    requesting_user = request.user
    recipe = personalize_if_user_not_owner(requesting_user, recipe)

    recipe.name = normalize(request.POST.get('name'))
    recipe.description = request.POST.get('description')
    recipe.prep_time = request.POST.get('prep')
    recipe.cook_time = request.POST.get('cook')
    recipe.servings = request.POST.get('servings')
    recipe.notes = request.POST.get('notes')
    recipe.author = request.POST.get('author')
    recipe.user = request.user
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

    recipe.save()

    if request.POST.get('add_to_recipe') != None:
        added_ingredient = Ingredient.objects.filter(ingredient = request.POST['ingredient_name'])
        if added_ingredient[0].id not in components_ingredients:
            ing = IngQuant(
                ingredient = added_ingredient[0],
                recipe = recipe
            )
            ing.save()
        # no else - alredy added to ingredients list
        return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe.id,)))
    
    if request.POST.get('add_ingredient') != None:
        return add_ingredient(request)
    
    if request.POST.get('save_ingredient') != None:
        ingredient_id = request.POST.get('save_ingredient')[16:]
        return add_ingredient(request, ingredient_id)
 
    return HttpResponseRedirect(reverse("recipes:detail", args=(recipe.id,)))
        

@login_required
def add_ingredient(request, ingredient_id = None):

    def add_ingredient_helper(ing, recipe, request):
        if request.POST.get('serving_size') != None:  ing.typical_serving_size = request.POST.get('serving_size')
        if request.POST.get('choose_unit') != None:  ing.typical_serving_unit = request.POST.get('choose_unit')
        if request.POST.get('weight_per_serving') != None:  ing.weight_per_serving = request.POST.get('weight_per_serving')
        if request.POST.get('protein') != None:  ing.protein = request.POST.get('protein')
        if request.POST.get('fat') != None:  ing.fat = request.POST.get('fat')
        if request.POST.get('carbs') != None:  ing.carbs = request.POST.get('carbs')
        if request.POST.get('calories') != None:  ing.calories = request.POST.get('calories')
        if request.POST.get('sugar') != None:  ing.sugar = request.POST.get('sugar')
        if request.POST.get('fiber') != None:  ing.fiber = request.POST.get('fiber')
        if request.POST.get('sodium') != None:  ing.sodium = request.POST.get('sodium')
        if request.POST.get('cholesterol') != None:  ing.cholesterol = request.POST.get('cholesterol')
        if request.POST.get('transfats') != None:  ing.transfats = request.POST.get('transfats')
        if request.POST.get('satfats') != None:  ing.satfats = request.POST.get('satfats')
        if request.POST.get('monounsatfats') != None:  ing.monounsatfats = request.POST.get('monounsatfats')
        if request.POST.get('polyunsatfats') != None:  ing.polyunsatfats = request.POST.get('polyunsatfats')
        
        ing.user = request.user
        ing.recipe = recipe
        
        ing.save()
        return ing

    # identify the recipe
    recipe_id = request.POST['recipe_id']
    recipe = Recipe.objects.get(pk = recipe_id)
    
    # initialize variables
    quantity = None
    unit = None

    if ingredient_id != None:
        ingredient_name = request.POST['add_ingredient_name_' + ingredient_id].strip().lower()
        # identify the initial ingquant from the recipe
        ingquant = IngQuant.objects.filter(recipe = recipe, ingredient = ingredient_id)
        if len(ingquant) > 0:
            # make sure to transfer quantity from prior inquant
            quantity = ingquant[0].quantity
            unit = ingquant[0].unit
        # delete old inquant
        ingquant.delete()
    else:
        ingredient_name = request.POST['add_ingredient_name'].strip().lower()
    
    # personalize ingredient name
    personalized_ingredient_name = "my " + ingredient_name
    added_ingredient = None

    # check to see if the ingredient name is in the database
    if Ingredient.objects.filter(ingredient = ingredient_name).count() != 0:
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
        added_ingredient = add_ingredient_helper(ingredient, recipe, request)
    # check to see if the personalized name is in the database
    elif Ingredient.objects.filter(ingredient = personalized_ingredient_name).count() !=0:
        # if the personalized ingredient already exists in the system
        ingredient = Ingredient.objects.filter(ingredient = personalized_ingredient_name)[0]
        added_ingredient = add_ingredient_helper(ingredient, recipe, request)
    # otherwise create a new ingredient
    else:
        ingredient = Ingredient(ingredient = ('my ' + ingredient_name))
        added_ingredient = add_ingredient_helper(ingredient, recipe, request)

    components_ingredients = []
    for component in recipe.get_ingquants():
        components_ingredients.append(component.ingredient.id)

    # create a new ingquant
    if added_ingredient.id not in components_ingredients:
        new_ingquant = IngQuant(
            ingredient = added_ingredient, 
            quantity = quantity,
            unit = unit,
            recipe = Recipe.objects.get(pk=recipe_id),
            )
        new_ingquant.save()
    else:
        update_ingquant = IngQuant.objects.filter(ingredient = added_ingredient.id, recipe = recipe)[0]
        update_ingquant.quantity = quantity
        update_ingquant.unit = unit
        update_ingquant.save()
    
    return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe_id,)))


@login_required
def shopping(request):
    
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
                new_ingquant.quantity = round(float(ingquant.quantity) + convert_quantity, 2) 
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
        recipe = shop.recipe
        query = recipe.get_ingquants()
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
        
    return render(request, 'recipes/shopping.html', {"shopping": shopping})
    

@login_required
def planning(request):
    return HttpResponse("TODO")


@login_required
def button_ajax(request):
    data = {'success': False} 
    if request.method=='POST':
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.objects.get(pk = recipe_id)
        action = request.POST.get('tag')
        action_dict = {
            'shop': Shop,
            'plan': Plan,
            'favorite': Favorites 
        }
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk = user_id)

        model = action_dict[action]
        
        match = model.objects.filter(recipe = recipe, user = user)
        if match.count() == 0:
            inst = model()
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
    recipe = Recipe.objects.get(pk = recipe_id)
    requesting_user = request.user
    if requesting_user == recipe.user:
        recipe.delete()
        return HttpResponseRedirect(reverse("recipes:index"))
    else:
        messages.info(request, 'You cannot delete a recipe that does not belong to you.')
        return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe_id,)))
    
def cancel(request):
    valuenext = request.POST.get('next')
    return HttpResponseRedirect(valuenext)
