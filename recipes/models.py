from django.db import models
from django.utils.translation import gettext_lazy as _ 
from .convert_units import convert_units
from django.contrib.auth.models import User

from tempt.settings import MEDIA_URL


VOLUME = ['ml', 'liter', 'tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon']
WEIGHT = ['g', 'kg', 'wtoz', 'lb']
UNIT = ["", "can"]


MEAL_CHOICES = (
    ("BREAKFAST", "breakfast"),
    ("SNACK", "snack"),
    ("MEAL", "meal"),
    ("DESSERT", "dessert"),
)

UNIT_CHOICES = (
    ("GRAM", "gram"),
    ("CUP", "cup"),
    ("TBSP", "tbsp"),
    ("TSP", "tsp"),
    ("WTOZ", "wt oz"),
    ("FLOZ", "fl oz"),
    ("ML", "ml"),
    ("CAN", "can"),
    ("GALLON", 'gallon'),
    ("KILO", "kilo"),
    ("LITER", "liter"),
    ("LB", "lb"),
    ("PINT", 'pint'),
    ("QUART", 'quart'),
    ("UNIT", "item"),
    ("UNDETERMINED", "?"),
)

CATEGORY_CHOICES = (
    ("ALCOHOLIC_BEVERAGES", 'alcoholic beverages'),
    ("BABY_FOODS", 'baby foods'),
    ("BAKED_PRODUCTS", 'baked goods'),
    ("BEEF_PRODUCTS", 'beef'),
    ("BEVERAGES", 'beverages'),
    ("BREAKFAST_CEREALS", 'breakfast cereals'),
    ("CEREAL_GRAINS_AND_PASTA", 'cereals, grains, and pasta'),
    ("DAIRY_AND_EGG_PRODUCTS", 'dairy and eggs'),
    ("FAST_FOODS", 'fastfoods'),
    ("FATS_AND_OILS", 'fats and oils'),
    ("FINFISH_AND_SHELLFISH_PRODUCTS", 'fish and shellfish'),
    ("FRUITS_AND_FRUIT_JUICES", 'fruits and fruit juices'),
    ("LAMB_VEAL_AND_GAME_PRODUCTS", 'lamb, veal, and game'),
    ("LEGUMES_AND_LEGUME_PRODUCTS", 'legumes'),
    ("MEALS_ENTREES_AND_SIDE_DISHES", 'prepared meals'),
    ("NUT_AND_SEED_PRODUCTS", 'nut and seed'),
    ("PORK_PRODUCTS", 'pork'),
    ("POULTRY_PRODUCTS", 'poultry'),
    ("RESTAURANT_FOODS", 'restaurant foods'),
    ("SAUSAGES_AND_LUNCHEON_MEATS", 'sausages and lunch meats'),
    ("SNACKS", 'snacks'),
    ("SOUPS_SAUCES_AND_GRAVIES", 'soups and sauces'),
    ("SPICES_AND_HERBS", 'spices and herbs'),
    ("SWEETS", 'sweets'),
    ("VEGETABLES_AND_VEGETABLE_PRODUCTS", 'vegetables'),
    ("OTHER", 'other'),
)


class Recipe(models.Model):
    name = models.CharField(max_length = 256)
    description = models.CharField(max_length = 1024, null = True, blank = True)
    prep_time = models.IntegerField(null = True, blank = True)
    cook_time = models.IntegerField(null = True, blank = True)
    servings = models.IntegerField(default = 4)
    photo = models.ImageField(upload_to = "recipes/", null = True, blank = True)
    notes = models.CharField(max_length = 2048, null = True, blank = True)
    # as written by user
    author = models.CharField(max_length = 150, default = "Anonymous")
    # if others are allowed to see the recipe
    public = models.BooleanField(default = False)
    # The user who uploaded the recipe
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # if the recipe is the original (false) or a personalized version of another (true)
    personalized = models.BooleanField(default = False)
    
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
    

    def get_steps(self):
        return Step.objects.filter(recipe = self.id).order_by('order')


    def get_ingquants(self):
        return IngQuant.objects.filter(recipe = self.id)


    def __str__(self):
        return self.name

    
    def favorite(self, user_id):
        if Favorites.objects.filter(self, user_id = user_id).count() > 0:
            return True
        else:
            return False

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


class Step(models.Model):
    step = models.CharField(max_length = 1024)
    order = models.IntegerField()
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

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

class IngQuant(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE)
    quantity = models.DecimalField(max_digits = 7, decimal_places = 2, default = 0)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE, null = True, blank = True)

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
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)

class Shop(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE) 

    def __str__(self):
        return str(self.recipe)

class Plan(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)
    
