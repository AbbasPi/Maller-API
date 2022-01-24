# Generated by Django 3.2.8 on 2022-01-21 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0017_auto_20220121_2213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(blank=True, null=True, related_name='products', to='commerce.Category', verbose_name='category'),
        ),
    ]
