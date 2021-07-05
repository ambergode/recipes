# Generated by Django 3.2 on 2021-05-26 01:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0019_auto_20210523_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('notes', models.CharField(blank=True, max_length=1024, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('days', models.IntegerField(default='7')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlannedMeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal', models.CharField(choices=[('DINNER', 'dinner'), ('SNACK', 'snack'), ('LUNCH', 'lunch'), ('OTHER', 'other'), ('BREAKFAST', 'breakfast'), ('DESSERT', 'dessert')], default='DINNER', max_length=10)),
                ('servings', models.IntegerField(default='2')),
                ('day', models.IntegerField()),
                ('ingredients', models.ManyToManyField(to='recipes.Ingredient')),
                ('meal_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.mealplan')),
                ('recipes', models.ManyToManyField(to='recipes.Recipe')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
