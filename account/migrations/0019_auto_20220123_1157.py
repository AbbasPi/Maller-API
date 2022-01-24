# Generated by Django 3.2.8 on 2022-01-23 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_alter_vendor_user_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.ImageField(upload_to='customer/', verbose_name='image'),
        ),
    ]
