from django.db import models
from django.utils.translation import gettext_lazy as _ 
from .convert_units import convert_units


VOLUME = ['ml', 'liter', 'tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon']
WEIGHT = ['g', 'kg', 'wtoz', 'lb']
UNIT = ["", "can"]


class Recipe(models.Model):
    name = models.CharField(max_length = 256)
    description = models.CharField(max_length = 1024)
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    servings = models.IntegerField(default = 4)
    photo = models.ImageField(upload_to = "recipes/static/recipe_imgs/")
    in_shopping = models.BooleanField(default="False")
    in_planning = models.BooleanField(default="False")

    class MealChoices(models.TextChoices):
        SNACK = "snack", _("snack")
        MEAL = "meal", _("meal")
        DESSERT = "dessert", _("dessert")
    
    snack_or_meal = models.CharField(
        max_length = 8,
        choices = MealChoices.choices,
        default = MealChoices.MEAL
    )

    def get_total_time(self):
        return self.cook_time + self.prep_time
    

    def get_steps(self):
        return Step.objects.filter(recipe = self.id)


    def get_ingquants(self):
        return IngQuant.objects.filter(recipe = self.id)


    def __str__(self):
        return self.name


class Step(models.Model):
    step = models.CharField(max_length = 1024)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    def __str__(self):
        return self.step


class Ingredient(models.Model):
    ingredient = models.CharField(max_length = 256, unique = True)

    class CategoryChoices(models.TextChoices):
        DAIRY_AND_EGG_PRODUCTS = 'dairy_and_egg_products', _('dairy and egg products')
        SPICES_AND_HERBS = 'spices_and_herbs', _('spices and herbs')
        BABY_FOODS = 'baby_foods', _('baby foods')
        FATS_AND_OILS = 'fats_and_oils', _('fats and oils')
        POULTRY_PRODUCTS = 'poultry_products', _('poultry products')
        SOUPS_SAUCES_AND_GRAVIES = 'soups_sauces_and_gravies', _('soups, sauces, and gravies')
        SAUSAGES_AND_LUNCHEON_MEATS = 'sausages_and_luncheon_meats', _('sausages and luncheon meats')
        BREAKFAST_CEREALS = 'breakfast_cereals', _('breakfast cereals')
        FRUITS_AND_FRUIT_JUICES = 'fruits_and_fruit_juices', _('fruits and fruit juices')
        PORK_PRODUCTS = 'pork_products', _('pork products')
        VEGETABLES_AND_VEGETABLE_PRODUCTS = 'vegetables_and_vegetable_products', _('vegetables and vegetable products')
        NUT_AND_SEED_PRODUCTS = 'nut_and_seed_products', _('nut and seed products')
        BEEF_PRODUCTS = 'beef_products', _('beef products')
        BEVERAGES = 'beverages', _('beverages')
        FINFISH_AND_SHELLFISH_PRODUCTS = 'finfish_and_shellfish_products', _('finfish and shellfish products')
        LEGUMES_AND_LEGUME_PRODUCTS = 'legumes_and_legume_products', _('legumes and legume products')
        LAMB_VEAL_AND_GAME_PRODUCTS = 'lamb_veal_and_game_products', _('lamb, veal, and game products')
        BAKED_PRODUCTS = 'baked_products', _('baked products')
        SWEETS = 'sweets', _('sweets')
        CEREAL_GRAINS_AND_PASTA = 'cereal_grains_and_pasta', _('cereal grains and pasta')
        FAST_FOODS = 'fast_foods', _('fast foods')
        MEALS_ENTREES_AND_SIDE_DISHES = 'meals_entrees_and_side_dishes', _('meals, entrees, and side dishes')
        SNACKS = 'snacks', _('snacks')
        AMERICAN_INDIAN_AND_ALASKA_NATIVE_FOODS = 'american_indian_and_alaska_native_foods', _('american indian and alaska native foods')
        RESTAURANT_FOODS = 'restaurant_foods', _('restaurant foods')
        BRANDED_FOOD_PRODUCTS_DATABASE = 'branded_food_products_database', _('branded food products database')
        QUALITY_CONTROL_MATERIALS = 'quality_control_materials', _('quality control materials')
        ALCOHOLIC_BEVERAGES = 'alcoholic_beverages', _('alcoholic beverages')
        OTHER = 'other', _('other')
        
    category = models.CharField(
        max_length = 256, 
        choices = CategoryChoices.choices,
        default = CategoryChoices.OTHER
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
    quantity = models.DecimalField(max_digits = 7, decimal_places = 2)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    class UnitChoices(models.TextChoices):
        GRAM = "gram", _("gram")
        WTOZ = "wt oz", _("wt oz")
        FLOZ = "fl oz", _("fl oz")
        CUP = "cup", _("cup")
        TSP = "tsp", _("tsp")
        TBSP = "tbsp", _("tbsp")
        ML = "ml", _("mL")
        UNIT = "", _("")
        CAN = "can", _("can")
        PINT = 'pint', _('pint')
        QUART = 'quart', _('quart')
        GALLON = 'gallon', _('gallon')
        LITER = "liter", _('liter')
        KILO = "kilo", _('kilo')
        LB = "lb", _('lb')
        UNDETERMINED = "undetermined", _('undetermined')


    unit = models.CharField(
        max_length = 13,
        choices = UnitChoices.choices,
        default = UnitChoices.GRAM
    )


    def __str__(self):
        unit = self.unit
        if self.quantity != 1 and unit != "":
            unit += "s"
        return str(self.ingredient) + " " + str(self.quantity) + " " + unit

