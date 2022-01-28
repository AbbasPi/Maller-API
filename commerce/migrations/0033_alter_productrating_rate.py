# Generated by Django 3.2.8 on 2022-01-27 17:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0032_alter_productrating_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrating',
            name='rate',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
