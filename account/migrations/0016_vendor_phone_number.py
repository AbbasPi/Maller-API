# Generated by Django 4.0.1 on 2022-01-18 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_remove_vendor_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='phone_number',
            field=models.CharField(default='', max_length=14, verbose_name='phone number'),
        ),
    ]
