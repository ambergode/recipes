# Generated by Django 3.2 on 2021-05-14 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_rename_private_recipe_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingquant',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]
