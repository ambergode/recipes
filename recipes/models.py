from django.db import models
from django.utils.translation import gettext_lazy as _ 


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
    ingredient = models.CharField(max_length = 100)
    
    # TODO Nutrition data

    def __str__(self):
        return self.ingredient


class IngQuant(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE)
    quantity = models.DecimalField(max_digits = 7, decimal_places = 2)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    class UnitChoices(models.TextChoices):
        GRAM = "gram", _("grams")
        OZ = "oz", _("oz")
        FLOZ = "fl oz", _("fl oz")
        CUP = "cup", _("cup")
        TSP = "tsp", _("tsp")
        TBSP = "tbsp", _("tbsp")
        ML = "ml", _("mL")
        UNIT = "", _("")


    unit = models.CharField(
        max_length = 5,
        choices = UnitChoices.choices,
        default = UnitChoices.GRAM
    )


    def __str__(self):
        unit = self.unit
        if self.quantity != 1 and unit != "":
            unit += "s"
        return str(self.ingredient) + " " + str(self.quantity) + " " + unit

