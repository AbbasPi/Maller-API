# Generated by Django 4.0.1 on 2022-01-20 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_vendor_phone_number'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commerce', '0010_alter_productrating_product_alter_productrating_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendorrating',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_rating', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='vendor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_rating', to='account.vendor'),
        ),
    ]
