# Generated by Django 3.2.7 on 2022-02-08 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0007_auto_20220208_1546'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='product',
        ),
        migrations.RemoveField(
            model_name='item',
            name='properties',
        ),
        migrations.DeleteModel(
            name='Property',
        ),
        migrations.DeleteModel(
            name='Variant',
        ),
    ]
