from django.contrib import admin

from .models import Recipe, Step, IngQuant, Ingredient

admin.site.register(Recipe)
admin.site.register(Step)
admin.site.register(IngQuant)
admin.site.register(Ingredient)
