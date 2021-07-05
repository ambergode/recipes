# Generated by Django 3.2 on 2021-05-26 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0023_auto_20210526_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plannedmeal',
            name='ingredients',
            field=models.ManyToManyField(blank=True, to='recipes.Ingredient'),
        ),
        migrations.AlterField(
            model_name='plannedmeal',
            name='recipes',
            field=models.ManyToManyField(blank=True, to='recipes.Recipe'),
        ),
    ]