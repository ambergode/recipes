from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader, RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from .models import Recipe, Ingredient, IngQuant, Step, Favorites, Shop, Plan
from .models import VOLUME, WEIGHT, UNIT, UNIT_CHOICES, MEAL_CHOICES, CATEGORY_CHOICES
from .convert_units import convert_units
from .forms import MealForm, UnitForm, CategoryForm, RecipePhotoForm


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
            if Recipe.objects.filter(name = new_recipe).count() > 0:
                ctx = {
                    "error_message": "is already in the database. Please use a unique name.",
                    "recipe": new_recipe
                }
                return render(request, 'recipes/create_recipe.html', ctx) 
                
            # if unique, create new recipe    
            else:
                new_recipe = Recipe(name = new_recipe)
                new_recipe.save()
                
        return HttpResponseRedirect(reverse("recipes:display_edit_recipe", kwargs= { "recipe_id": new_recipe.id, }))
    else:
        return render(request, 'recipes/create_recipe.html', context = {})


@login_required
def display_edit_recipe(request, recipe_id):
    recipe = Recipe.objects.get(pk = recipe_id)
    components = []
    
    ctx = { 
        "recipe": recipe, 
        "meal_form": MealForm(initial={'type_of_meal': recipe.snack_or_meal.upper()}), 
        "recipe_id": recipe_id, 
        "photo_form": RecipePhotoForm(),
    }

    ingquants = recipe.get_ingquants()
    for ingquant in ingquants:
        form = UnitForm(initial={'choose_unit': ingquant.unit.upper()}, prefix="name_" + str(ingquant.id))
        components.append((ingquant, form))
    ctx["components"] = components

    steps = recipe.get_steps()
    if steps.count() > 0:
        ctx['steps'] = steps
        ctx['step_count'] = steps.count()
    
    ingredients = None
    url_parameter = request.GET.get("q")
    ctx["search"] = url_parameter
    if url_parameter:
        url_parameters = url_parameter.split()
        args = []
        for param in url_parameters:
            param = param.strip(", /-")
            args.append(Q(ingredient__icontains=param))
        ingredients = Ingredient.objects.filter(*args)
        ctx["ingredients"] = ingredients

    if request.is_ajax():
        ctx['searched'] = True
        if ctx['ingredients'].count() == 0:
            ctx['new_ing_unit_form'] = UnitForm()
            ctx['category_form'] = CategoryForm()
            template = loader.get_template('recipes/add_ingredient.html')
            context = ctx
            html = template.render(context, request)
        else:
            template = loader.get_template('recipes/ingredient_list.html')
            context = ctx
            html = template.render(context, request)
        data_dict = {
            "html_from_view": html, 
            "number_ingredients": ctx['ingredients'].count(),
        }
        return JsonResponse(data=data_dict, safe=False)

    return render(request, 'recipes/edit_recipe.html', context = ctx)


@login_required
def record_edit_recipe(request, recipe_id):
        
    recipe = Recipe.objects.get(pk = recipe_id)

    recipe.name = request.POST['name']
    recipe.snack_or_meal = request.POST['type_of_meal'].upper()
    recipe.description = request.POST['description']
    recipe.prep_time = request.POST['prep']
    recipe.cook_time = request.POST['cook']
    recipe.servings = request.POST['servings']
    photo_form = RecipePhotoForm(request.POST, request.FILES)
    recipe.notes = request.POST['notes']
    recipe.author = request.POST['author']
    recipe.user = request.user
    if request.POST['public'] == 'on':
        recipe.public = True
    else:
        recipe.public = False

    if photo_form.is_valid():
        if photo_form.cleaned_data.get('photo') != None:
            recipe.photo = photo_form.cleaned_data.get('photo')
    
    # in_shopping
    # in_planning
    # favorite

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

    try:
        if request.POST['add_to_recipe']:
            added_ingredient = Ingredient.objects.filter(ingredient = request.POST['ingredient_name'])
            if added_ingredient[0].id not in components_ingredients:
                ing = IngQuant(
                    ingredient = added_ingredient[0],
                    recipe = recipe
                )
                ing.save()
            else:
                print("Added ingredient already in list.")
            return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe.id,)))
    except:
        pass
    
    return HttpResponseRedirect(reverse("recipes:detail", args=(recipe.id,)))
        

@login_required
def add_ingredient(request):

    recipe_id = request.POST['recipe_id']
    recipe = Recipe.objects.get(pk = recipe_id)

    ingredient_name = request.POST['ingredient_name']
    if Ingredient.objects.filter(ingredient = ingredient_name).count() == 0:
        new_ingredient = Ingredient(
            ingredient = request.POST['ingredient_name'],
            category = request.POST['choose_category'],
            typical_serving_size = request.POST['serving_size'],
            typical_serving_unit = request.POST['choose_unit'], 
            weight_per_serving = request.POST['weight_per_serving'], 
            protein = request.POST['protein'], 
            fat = request.POST['fat'], 
            carbs = request.POST['carbs'], 
            calories = request.POST['calories'], 
            sugar = request.POST['sugar'],   
            fiber = request.POST['fiber'], 
            sodium = request.POST['sodium'], 
            cholesterol = request.POST['cholesterol'], 
            transfats = request.POST['transfats'], 
            satfats = request.POST['satfats'], 
            monounsatfats = request.POST['monounsatfats'], 
            polyunsatfats = request.POST['polyunsatfats']
        )

        new_ingredient.save()
    else:
        new_ingredient = Ingredient.objects.filter(ingredient = ingredient_name)[0]
    
    components_ingredients = []
    for component in recipe.get_ingquants():
        components_ingredients.append(component.ingredient.id)

    added_ingredient = Ingredient.objects.filter(ingredient = new_ingredient)
    if added_ingredient[0].id not in components_ingredients:
        new_ingquant = IngQuant(
                ingredient = new_ingredient, 
                recipe = Recipe.objects.get(pk=recipe_id),
            )
        new_ingquant.save()
    
    return HttpResponseRedirect(reverse("recipes:display_edit_recipe", args=(recipe_id,)))


@login_required
def shopping(request):
    recipes = Recipe.objects.all()

    # create empty dictionary for shopping list
    shopping_list = {}
    for recipe in recipes:
        # check if it's in the shopping list
        if recipe.in_shopping:
            # get ingredients of each recipe
            ingquants = recipe.get_ingquants()
            for ingquant in ingquants:
                # check if ingredients already in shopping list
                if ingquant.ingredient in shopping_list.keys():
                    # if in dictionary already, check if units match
                    if shopping_list[ingquant.ingredient][1] != ingquant.unit:
                    # if units don't match, complete correct conversion    
                        quantity = convert_units(ingquant.quantity, ingquant.unit, shopping_list[ingquant.ingredient][1])
                    # add quantities to dictionary
                    shopping_list[ingquant.ingredient][0] += quantity
                # if not in dictionary already, add ingredient and tuple for quantity and unit
                else:
                    shopping_list[ingquant.ingredient] = [ingquant.quantity, ingquant.unit]

    return render(request, 'recipes/shopping.html', {"shopping_list": shopping_list})


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