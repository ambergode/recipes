from django.db import models
from django.utils.translation import gettext_lazy as _ 
from .convert_units import convert_units

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
    ("WTOZ", "wt oz"),
    ("FLOZ", "fl oz"),
    ("CUP", "cup"),
    ("TSP", "tsp"),
    ("TBSP", "tbsp"),
    ("ML", "ml"),
    ("CAN", "can"),
    ("PINT", 'pint'),
    ("QUART", 'quart'),
    ("GALLON", 'gallon'),
    ("LITER", "liter"),
    ("KILO", "kilo"),
    ("LB", "lb"),
    ("UNIT", "item"),
    ("UNDETERMINED", "undetermined"),
)

CATEGORY_CHOICES = (
    ("DAIRY_AND_EGG_PRODUCTS", 'dairy and eggs'),
    ("SPICES_AND_HERBS", 'spices and herbs'),
    ("BABY_FOODS", 'baby foods'),
    ("FATS_AND_OILS", 'fats and oils'),
    ("POULTRY_PRODUCTS", 'poultry'),
    ("SOUPS_SAUCES_AND_GRAVIES", 'soups and sauces'),
    ("SAUSAGES_AND_LUNCHEON_MEATS", 'sausages and lunch meats'),
    ("BREAKFAST_CEREALS", 'breakfast cereals'),
    ("FRUITS_AND_FRUIT_JUICES", 'fruits and fruit juices'),
    ("PORK_PRODUCTS", 'pork'),
    ("VEGETABLES_AND_VEGETABLE_PRODUCTS", 'vegetables'),
    ("NUT_AND_SEED_PRODUCTS", 'nut and seed'),
    ("BEEF_PRODUCTS", 'beef'),
    ("BEVERAGES", 'beverages'),
    ("FINFISH_AND_SHELLFISH_PRODUCTS", 'fish and shellfish'),
    ("LEGUMES_AND_LEGUME_PRODUCTS", 'legumes'),
    ("LAMB_VEAL_AND_GAME_PRODUCTS", 'lamb, veal, and game'),
    ("BAKED_PRODUCTS", 'baked goods'),
    ("SWEETS", 'sweets'),
    ("CEREAL_GRAINS_AND_PASTA", 'cereals, grains, and pasta'),
    ("FAST_FOODS", 'fastfoods'),
    ("MEALS_ENTREES_AND_SIDE_DISHES", 'prepared meals'),
    ("SNACKS", 'snacks'),
    ("RESTAURANT_FOODS", 'restaurant foods'),
    ("ALCOHOLIC_BEVERAGES", 'alcoholic beverages'),
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

    @property
    def favorite(self):
        if Favorites.objects.filter(recipe = self).count() > 0:
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
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

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
        return str(self.ingredient) + " " + str(self.quantity) + " "

class Favorites(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)

class Shop(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)

class Plan(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.recipe)
    
