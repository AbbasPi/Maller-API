# Generated by Django 3.2.8 on 2022-01-25 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_remove_customer_image'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Customer',
        ),
    ]