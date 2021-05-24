from django.test import TestCase

from recipes.models import Recipe, Ingredient, IngQuant, Step
from recipes.views import detail

class NutritionDataTest(TestCase):
    def setUp(self):
        Recipe.object.create(name='Tacos')
        Ingredient.object.create(
            ingredient='cheese'
            calories= 100,
            fat= 13,
            satfats= 4,
            transfats= 3, 
            monounsatfats= 2,
            polyunsatfats= 1, 
            cholesterol= 5, 
            sodium= 6,
            carbs= 15,
            fiber= 7,
            sugar= 8,
            protein= 9,
            user= None
        )
        Ingredient.object.create(
            ingredient='lettuce'
            calories= 50,
            fat= 1,
            satfats= 2,
            transfats= 3, 
            monounsatfats= 4,
            polyunsatfats= 5, 
            cholesterol= 6, 
            sodium= 7,
            carbs= 8,
            fiber= 9,
            sugar= 10,
            protein= 11,
            user= None
        )
        Ingredient.object.create(
            ingredient='shell'
            calories= 150,
            fat= 1,
            satfats= 2,
            transfats= 3, 
            monounsatfats= 4,
            polyunsatfats= 5, 
            cholesterol= 6, 
            sodium= 7,
            carbs= 8,
            fiber= 9,
            sugar= 10,
            protein= 11,
            user= 1
        )

class NutritionInformationTest(TestCase):
    def setUp(self):
        recipe = Recipe.objects.create(name='veggie burgers', servings=39, snack_or_meal="MEAL")

        ingredient_list = [
            ['64', 'oz', 'mushrooms, portabella, raw'],
            ['14', 'gram', 'my oil, olive, extra virgin'],
            ['87', 'oz', 'beans, black, mature seeds, canned, low sodium'],
            ['30', 'oz', 'onions, red, raw'],
            ['18', 'item', 'eggs, grade a, large, egg whole'],
            ['30', 'gram', 'garlic, raw'],
            ['10', 'gram', 'sauce, worcestershire'],
            ['85', 'gram', 'sauce, steak, tomato based'],
            ['21', 'oz', 'cheese, parmesan, grated'],
            ['320', 'gram', 'cereals, oats, regular and quick, not fortified, dry'],
            ['40', 'ml', 'my liquid aminos'],
        ]
        for ingredient in ingredient_list:
            ingredient = Ingredient.objects.filter(ingredient = ingredient[2])
            IngQuant.objects.create(ingredient=ingredient, quantity=int(ingredient[0]), recipe=recipe, unit=ingredient[1])
    
    def test_nutrition_facts:
        actual_nutrition = {
            'calories': 215,
            'fat': 8,
            'satfats': 3,
            'transfats': 0, 
            'monounsatfats': 2,
            'polyunsatfats': 1, 
            'cholesterol': 0, 
            'sodium': 500,
            'carbs': 23,
            'fiber': 7,
            'sugar': 1,
            'protein': 14,
        }
        detail = detail(request, recipe.id)
        for key in actual_nutrition.keys():
            self.assertEqual(actual_nutrition[key],)


from django.test import TestCase
from myapp.models import Animal

class AnimalTestCase(TestCase):
    def setUp(self):
        Animal.objects.create(name="lion", sound="roar")
        Animal.objects.create(name="cat", sound="meow")

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')