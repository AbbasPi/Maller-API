# Generated by Django 3.2.8 on 2022-01-27 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0028_remove_order_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='height',
            field=models.FloatField(blank=True, null=True, verbose_name='height'),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.FloatField(blank=True, null=True, verbose_name='length'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, null=True, verbose_name='weight'),
        ),
        migrations.AddField(
            model_name='product',
            name='width',
            field=models.FloatField(blank=True, null=True, verbose_name='width'),
        ),
    ]
