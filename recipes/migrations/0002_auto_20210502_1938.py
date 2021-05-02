# Generated by Django 3.2 on 2021-05-02 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='snack_or_meal',
            field=models.CharField(choices=[('snack', 'snack'), ('meal', 'meal'), ('dessert', 'dessert')], default='meal', max_length=8),
        ),
        migrations.AlterField(
            model_name='ingquant',
            name='unit',
            field=models.CharField(choices=[('gram', 'grams'), ('oz', 'oz'), ('fl oz', 'fl oz'), ('cup', 'cup'), ('tsp', 'tsp'), ('tbsp', 'tbsp'), ('ml', 'mL'), ('', '')], default='gram', max_length=5),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='photo',
            field=models.ImageField(upload_to='recipes/static/recipe_imgs/'),
        ),
    ]