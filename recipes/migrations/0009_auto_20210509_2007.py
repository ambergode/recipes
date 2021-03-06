# Generated by Django 3.2 on 2021-05-10 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20210507_2116'),
    ]

    operations = [
        migrations.AddField(
            model_name='step',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='snack_or_meal',
            field=models.CharField(choices=[('breakfast', 'breakfast'), ('snack', 'snack'), ('meal', 'meal'), ('dessert', 'dessert')], default='meal', max_length=10),
        ),
    ]
