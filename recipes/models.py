from django.db import models
from django.utils.translation import gettext_lazy as _ 


class Recipe(models.Model):
    name = models.CharField(max_length = 256)
    description = models.CharField(max_length = 1024)
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    servings = models.IntegerField(default = 4)
    photo = models.ImageField(upload_to = "recipes/static/recipe_imgs/")

    def get_total_time(self):
        return self.cook_time + self.prep_time
    
    def get_steps(self):
        steps = {}
        return Step.objects.filter(recipe = self.id)

    def __str__(self):
        return self.name


class Step(models.Model):
    step = models.CharField(max_length = 1024)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    def __str__(self):
        return self.step


class Ingredient(models.Model):
    ingredient = models.CharField(max_length = 100)
    
    # Nutrition data

    def __str__(self):
        return self.ingredient


class IngQuant(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE)
    quantity = models.DecimalField(max_digits = 7, decimal_places = 2)
    recipe = models.ForeignKey(Recipe, on_delete = models.CASCADE)

    class UnitChoices(models.TextChoices):
        GRAM = "G", _("grams")
        OZ = "OZ", _("oz")
        FLOZ = "FLOZ", _("fl oz")
        CUP = "CUP", _("cup")
        TSP = "TSP", _("tsp")
        TBSP = "TBSP", _("tbsp")
        ML = "ML", _("mL")
        UNIT = "UNIT", _("unit")


    unit = models.CharField(
        max_length = 5,
        choices = UnitChoices.choices,
        default = UnitChoices.GRAM
    )

    def __str__(self):
        return str(self.ingredient) + " " + str(self.quantity) + " " + self.unit



