from django import forms

from .models import Recipe, MEAL_CHOICES, UNIT_CHOICES, CATEGORY_CHOICES


class MealForm(forms.Form):
    type_of_meal = forms.ChoiceField(choices = MEAL_CHOICES, label='')

class UnitForm(forms.Form):
    choose_unit = forms.ChoiceField(choices = UNIT_CHOICES, label='')
    ingquant = forms.IntegerField(label='', widget=forms.HiddenInput())

class CategoryForm(forms.Form):
    choose_category = forms.ChoiceField(choices = CATEGORY_CHOICES, label='')

class RecipePhotoForm(forms.ModelForm):
    photo = forms.ImageField(required = False, label="")
    class Meta:
        model = Recipe
        fields = ['photo']