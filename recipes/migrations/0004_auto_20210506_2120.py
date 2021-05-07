# Generated by Django 3.2 on 2021-05-07 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20210502_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='calories',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='carbs',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='category',
            field=models.CharField(choices=[('dairy_and_egg_products', 'dairy and egg products'), ('spices_and_herbs', 'spices and herbs'), ('baby_foods', 'baby foods'), ('fats_and_oils', 'fats and oils'), ('poultry_products', 'poultry products'), ('soups_sauces_and_gravies', 'soups, sauces, and gravies'), ('sausages_and_luncheon_meats', 'sausages and luncheon meats'), ('breakfast_cereals', 'breakfast cereals'), ('fruits_and_fruit_juices', 'fruits and fruit juices'), ('pork_products', 'pork products'), ('vegetables_and_vegetable_products', 'vegetables and vegetable products'), ('nut_and_seed_products', 'nut and seed products'), ('beef_products', 'beef products'), ('beverages', 'beverages'), ('finfish_and_shellfish_products', 'finfish and shellfish products'), ('legumes_and_legume_products', 'legumes and legume products'), ('lamb_veal_and_game_products', 'lamb, veal, and game products'), ('baked_products', 'baked products'), ('sweets', 'sweets'), ('cereal_grains_and_pasta', 'cereal grains and pasta'), ('fast_foods', 'fast foods'), ('meals_entrees_and_side_dishes', 'meals, entrees, and side dishes'), ('snacks', 'snacks'), ('american_indian_and_alaska_native_foods', 'american indian and alaska native foods'), ('restaurant_foods', 'restaurant foods'), ('branded_food_products_database', 'branded food products database'), ('quality_control_materials', 'quality control materials'), ('alcoholic_beverages', 'alcoholic beverages'), ('other', 'other')], default='other', max_length=256),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='cholesterol',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='fat',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='fiber',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='monounsatfats',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='polyunsatfats',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='protein',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='satfats',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='sodium',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='sugar',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='transfats',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='typical_serving_size',
            field=models.DecimalField(decimal_places=3, default=None, max_digits=20),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='typical_serving_unit',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='weight_per_serving',
            field=models.DecimalField(decimal_places=3, default=None, max_digits=20),
        ),
        migrations.AlterField(
            model_name='ingquant',
            name='unit',
            field=models.CharField(choices=[('gram', 'gram'), ('wt oz', 'wt oz'), ('fl oz', 'fl oz'), ('cup', 'cup'), ('tsp', 'tsp'), ('tbsp', 'tbsp'), ('ml', 'mL'), ('', ''), ('can', 'can'), ('pint', 'pint'), ('quart', 'quart'), ('gallon', 'gallon'), ('liter', 'liter'), ('kilo', 'kilo'), ('lb', 'lb')], default='gram', max_length=7),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='ingredient',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]
