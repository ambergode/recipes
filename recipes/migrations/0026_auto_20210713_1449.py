# Generated by Django 3.2 on 2021-07-13 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0025_auto_20210703_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorites',
            name='mealplan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.mealplan'),
        ),
        migrations.AddField(
            model_name='shop',
            name='mealplan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.mealplan'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]
