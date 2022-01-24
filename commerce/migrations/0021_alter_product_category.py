# Generated by Django 3.2.8 on 2022-01-21 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0020_auto_20220121_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='products', to='commerce.Category', verbose_name='category'),
        ),
    ]
