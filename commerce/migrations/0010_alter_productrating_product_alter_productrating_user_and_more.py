# Generated by Django 4.0.1 on 2022-01-20 10:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0016_vendor_phone_number'),
        ('commerce', '0009_alter_product_merchant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrating',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='commerce.product'),
        ),
        migrations.AlterField(
            model_name='productrating',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='rate',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='vendor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.vendor'),
        ),
    ]
