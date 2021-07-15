from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import User

from tempt.settings import MEDIA_URL

from .convert_units import convert_units


VOLUME = ['ml', 'liter', 'tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon']
WEIGHT = ['g', 'kg', 'wtoz', 'lb']
UNIT = ["", "can"]


MEAL_CHOICES = (
    ("BREAKFAST", "breakfast"),
    ("SNACK", "snack"),
    ("MEAL", "meal"),
    ("DESSERT", "dessert"),
)


MEALTIME_CHOICES = (
    ('BREAKFAST', 'breakfast'),
    ('BRUNCH', 'brunch'),
    ('LUNCH', 'lunch'),
    ('DINNER', 'dinner'),
    ('SNACK', 'snack'),
    ('DESSERT', 'dessert'),
    ('OTHER', 'other'),
)


UNIT_CHOICES = (
    ("GRAM", "gram"),
    ("CUP", "cup"),
    ("TBSP", "tbsp"),
    ("TSP", "tsp"),
    ("WTOZ", "oz"),
    ("FLOZ", "fl oz"),
    ("ML", "ml"),
    ("CAN", "can"),
    ("GALLON", 'gallon'),
    ("KILO", "kilo"),
    ("LITER", "liter"),
    ("LB", "lb"),
    ("PINT", 'pint'),
    ("QUART", 'quart'),
    ("UNIT", ""),
    ("UNDETERMINED", "?"),
)


CATEGORY_CHOICES = (
    ("ALCOHOLIC_BEVERAGES", 'alcoholic beverages'),
    ("BABY_FOODS", 'baby foods'),
    ("BAKED_PRODUCTS", 'baked products'),
    ("BEEF_PRODUCTS", 'beef products'),
    ("BEVERAGES", 'beverages'),
    ("BREAKFAST_CEREALS", 'breakfast cereals'),
    ("CEREAL_GRAINS_AND_PASTA", 'cereal grains and pasta'),
    ("DAIRY_AND_EGG_PRODUCTS", 'dairy and egg products'),
    ("FAST_FOODS", 'fast foods'),
    ("FATS_AND_OILS", 'fats and oils'),
    ("FINFISH_AND_SHELLFISH_PRODUCTS", 'finfish and shellfish products'),
    ("FRUITS_AND_FRUIT_JUICES", 'fruits and fruit juices'),
    ("LAMB_VEAL_AND_GAME_PRODUCTS", 'lamb, veal, and game products'),
    ("LEGUMES_AND_LEGUME_PRODUCTS", 'legumes and legume products'),
    ("MEALS_ENTREES_AND_SIDE_DISHES", 'meals, entrees, and side dishes'),
    ("NUT_AND_SEED_PRODUCTS", 'nut and seed products'),
    ("PORK_PRODUCTS", 'pork products'),
    ("POULTRY_PRODUCTS", 'poultry products'),
    ("RESTAURANT_FOODS", 'restaurant foods'),
    ("SAUSAGES_AND_LUNCHEON_MEATS", 'sausages and lunch meats'),
    ("SNACKS", 'snacks'),
    ("SOUPS_SAUCES_AND_GRAVIES", 'soups, sauces, and gravies'),
    ("SPICES_AND_HERBS", 'spices and herbs'),
    ("SWEETS", 'sweets'),
    ("VEGETABLES_AND_VEGETABLE_PRODUCTS", 'vegetables and vegetable products'),
    ("AMERICAN_INDIAN_ALASKAN_NATIVE_FOODS", 'american indian/alaska native foods'),
    ("OTHER", 'other'),
)


UNIT_DICT = {
    "gram" : "GRAM",
    "cup" : "CUP",
    "tbsp" : "TBSP",
    "tsp" : "TSP",
    "oz" : "WTOZ",
    "fl oz" : "FLOZ",
    "ml" : "ML",
    "can" : "CAN",
    "gallon" : "GALLON",
    "kilo" : "KILO",
    "liter" : "LITER",
    "lb" : "LB",
    "pint" : "PINT",
    "quart" : "QUART",
    "" : "UNIT",
    "?" : "UNDETERMINED",
}


CATEGORY_DICT = {
    "ALCOHOLIC_BEVERAGES": 'alcoholic beverages',
    "BABY_FOODS": 'baby foods',
    "BAKED_PRODUCTS": 'baked products',
    "BEEF_PRODUCTS": 'beef products',
    "BEVERAGES": 'beverages',
    "BREAKFAST_CEREALS": 'breakfast cereals',
    "CEREAL_GRAINS_AND_PASTA": 'cereal grains and pasta',
    "DAIRY_AND_EGG_PRODUCTS": 'dairy and egg products',
    "FAST_FOODS": 'fast foods',
    "FATS_AND_OILS": 'fats and oils',
    "FINFISH_AND_SHELLFISH_PRODUCTS": 'finfish and shellfish products',
    "FRUITS_AND_FRUIT_JUICES": 'fruits and fruit juices',
    "LAMB_VEAL_AND_GAME_PRODUCTS": 'lamb, veal, and game products',
    "LEGUMES_AND_LEGUME_PRODUCTS": 'legumes and legume products',
    "MEALS_ENTREES_AND_SIDE_DISHES": 'meals, entrees, and side dishes',
    "NUT_AND_SEED_PRODUCTS": 'nut and seed products',
    "PORK_PRODUCTS": 'pork products',
    "POULTRY_PRODUCTS": 'poultry products',
    "RESTAURANT_FOODS": 'restaurant foods',
    "SAUSAGES_AND_LUNCHEON_MEATS": 'sausages and lunch meats',
    "SNACKS": 'snacks',
    "SOUPS_SAUCES_AND_GRAVIES": 'soups, sauces, and gravies',
    "SPICES_AND_HERBS": 'spices and herbs',
    "SWEETS": 'sweets',
    "VEGETABLES_AND_VEGETABLE_PRODUCTS": 'vegetables and vegetable products',
    "AMERICAN_INDIAN_ALASKAN_NATIVE_FOODS": 'american indian/alaska native foods',
    "OTHER": 'other',
}


class CommonInfo(models.Model):
    name = models.CharField(max_length = 256)
    description = models.CharField(max_length = 1024, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        abstract = True

    @property
    def in_shopping(self):
        if Shop.objects.filter(recipe = self).count() > 0:
            return True
        else:
            return False

    @property
    def in_plan(self):
        if Plan.objects.filter(recipe = self).count() > 0:
            return True
        else:
            return False
    
    def __str__(self):
        return self.name


class ShoppingList(CommonInfo):
    
    def get_ingquants(self):
        return IngQuant.objects.filter(shopping_list = self.id)

class Recipe(CommonInfo):
    prep_time = models.IntegerField(null = True, blank = True)
    cook_time = models.IntegerField(null = True, blank = True)
    servings = models.IntegerField(default = 4)
    photo = models.ImageField(upload_to = "recipes/", null = True, blank = True)
    notes = models.CharField(max_length = 2048, null = True, blank = True)
    # as written by user
    author = models.CharField(max_length = 150, default = "Anonymous")
    # if others are allowed to see the recipe
    public = models.BooleanField(default = False)
    # if the recipe is the original (false) or a personalized version of another (true)
    personalized = models.BooleanField(default = False)
    # the recipe will always keep the original inputs for servings and quantities
    # temp_servings allows users to change servings without accumulated rounding errors over time
    
    snack_or_meal = models.CharField(
        max_length = 10,
        choices = MEAL_CHOICES,
        default = 'MEAL'
    )

    def get_total_time(self):
        if self.cook_time and self.prep_time:
            return self.cook_time + self.prep_time
        else:
            return '--'
    
    def get_ingquants(self):
        return IngQuant.objects.filter(recipe = self.id)


    def get_steps(self):
        return Step.objects.filter(recipe = self.id).order_by('order')


    def favorite(self, user_id):
        if Favorites.objects.filter(self, user_id = user_id).count() > 0:
            return True
        else:
            return False


class Step(models.Model):
    step = models.CharField(max_length = 1024)
    order = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, related_name='steps')

    def __str__(self):
        return str(self.order + 1) + ". " + self.step


class Ingredient(models.Model):
    ingredient = models.CharField(max_length = 256, unique = True)
    user = models.ForeignKey(User, on_delete= models.CASCADE, null=True, blank=True)

    category = models.CharField(
        max_length = 256, 
        choices = CATEGORY_CHOICES,
        default = "OTHER"
    )

    # Typical serving size
    typical_serving_size = models.DecimalField(max_digits = 20, decimal_places = 3, null = True, blank = True, default = 0)
    typical_serving_unit = models.CharField(max_length = 50, null = True, blank = True, default = "undefined")
    
    # weight_per_serving measured in grams
    weight_per_serving = models.DecimalField(max_digits = 20, decimal_places = 3, null = True, blank = True, default = 0)

    # multiply typical serving size and weignt per serving by 1 / typical serving size
    def volume_per_100_g(self): 
        """ 
        Determines volume per 100g
        returns -1 if cannot convert
        """
        if self.weight_per_serving == 0 or self.typical_serving_unit == 0:
            return -1
        if self.typical_serving_unit in WEIGHT:
            return convert_units(self.typical_serving_size, self.typical_serving_unit, "ml")
        elif self.typical_serving_unit in VOLUME:
            try:
                converted_weight = self.weight_per_serving * (1 / self.typical_serving_size)
                return convert_units(self.weight_per_serving, converted_weight, "ml")
            except:
                pass 
        return -1

    # all nutrition data defined in terms of 100g of product, measured in grams
    # except sodium, cholesterol measured in mg, calories measured in kcal
    def __nutrient_field():
        return models.DecimalField(max_digits = 20, decimal_places = 3, default = 0)

    protein = __nutrient_field()
    fat = __nutrient_field()
    carbs = __nutrient_field()
    calories = __nutrient_field()
    sugar = __nutrient_field()
    fiber = __nutrient_field()
    sodium = __nutrient_field()
    cholesterol = __nutrient_field()
    transfats = __nutrient_field()
    satfats = __nutrient_field()
    monounsatfats = __nutrient_field()
    polyunsatfats = __nutrient_field()

    def __str__(self):
        return self.ingredient


class MealPlan(models.Model):
    name = models.CharField(max_length = 256)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length = 1024, null = True, blank = True)
    start_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    days = models.IntegerField(default = '7')
    people = models.IntegerField(default = '2')

    def __meal_field():
        return models.BooleanField(default = False)

    breakfast = __meal_field()
    brunch = __meal_field()
    lunch = __meal_field()
    dinner = __meal_field()
    snack = __meal_field()
    dessert = __meal_field()
    other = __meal_field()

    def __str__(self):
        return self.name 

    def get_recipe_amounts(self):
        # make a dictionary: {recipe: servings}
        recipe_list = {}
        for pm in self.planned_meals.all():
            for recipe in pm.recipes.all():
                if recipe in recipe_list.keys():
                    recipe_list[recipe] += pm.servings
                else:
                    recipe_list[recipe] = pm.servings         
        return recipe_list
    

class PlannedMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    meal_plan = models.ForeignKey(MealPlan, on_delete = models.CASCADE, related_name = 'planned_meals')
    meal = models.CharField(
        max_length = 10,
        choices = MEALTIME_CHOICES,
        default = "DINNER"
    )
    servings = models.IntegerField(default = '2')
    day = models.IntegerField()
    recipes = models.ManyToManyField(Recipe, blank = True)
    notes = models.CharField(max_length = 226, null = True, blank = True)

    def __str__(self):
        return 'day ' + str(self.day) + ' ' + self.meal + ' for ' + str(self.meal_plan)



class IngQuant(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE, related_name = 'ingredients')
    quantity = models.DecimalField(max_digits = 32, decimal_places = 8, default = 0)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, null = True, blank = True, related_name = 'ingquants')
    shopping_list = models.ForeignKey(ShoppingList, on_delete = models.CASCADE, null = True, blank = True, related_name = 'ingquants')
    meal_plan = models.ForeignKey(MealPlan, on_delete = models.CASCADE, null = True, blank = True, related_name = 'ingquants')

    unit = models.CharField(
        max_length = 13,
        choices = UNIT_CHOICES,
        default = "GRAM"
    )

    def unitDisplay(self):
        return self.get_unit_display()

    def __str__(self):
        unit = self.unit.lower()
        if self.quantity != 1 and unit != "":
            unit += "s"
        return str(self.ingredient) + " " + str(self.quantity) + " " + str(self.unit)


class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, null = True, blank = True)
    mealplan = models.ForeignKey(MealPlan, on_delete = models.CASCADE, null = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'favorites')

    def __str__(self):
        if self.recipe:
            return str(self.recipe)
        else:
            return str(self.mealplan)

class Shop(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, null = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE) 
    shopping_list = models.ForeignKey(ShoppingList, on_delete = models.CASCADE, null = True, blank = True)
    mealplan = models.ForeignKey(MealPlan, on_delete = models.CASCADE, null = True, blank = True)

    def __str__(self):
        if self.recipe:
            return str(self.recipe)
        elif self.shopping_list:
            return str(self.shopping_list)
        else:
            return str(self.mealplan)

class Plan(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, null = True, blank = True)
    shopping_list = models.ForeignKey(ShoppingList, on_delete = models.CASCADE, null = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)


