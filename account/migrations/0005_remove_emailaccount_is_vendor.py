# Generated by Django 3.2.7 on 2022-03-01 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_emailaccount_is_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailaccount',
            name='is_vendor',
        ),
    ]