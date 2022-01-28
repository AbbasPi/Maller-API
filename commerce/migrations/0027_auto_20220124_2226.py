# Generated by Django 3.2.8 on 2022-01-24 19:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0026_alter_productrating_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrating',
            name='rate',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)]),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='rate',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
