# Generated by Django 3.2 on 2021-07-03 22:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0024_auto_20210526_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealplan',
            name='brunch',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ingquant',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='ingquant',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingquants', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='ingquant',
            name='shopping_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingquants', to='recipes.shoppinglist'),
        ),
        migrations.AlterField(
            model_name='plannedmeal',
            name='meal',
            field=models.CharField(choices=[('BREAKFAST', 'breakfast'), ('BRUNCH', 'brunch'), ('LUNCH', 'lunch'), ('DINNER', 'dinner'), ('SNACK', 'snack'), ('DESSERT', 'dessert'), ('OTHER', 'other')], default='DINNER', max_length=10),
        ),
        migrations.AlterField(
            model_name='plannedmeal',
            name='meal_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planned_meals', to='recipes.mealplan'),
        ),
    ]
