# Generated by Django 3.2.7 on 2022-02-10 22:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_vendor'),
        ('commerce', '0013_alter_product_qty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='account.vendor', verbose_name='vendor'),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_rating', to='account.vendor'),
        ),
        migrations.DeleteModel(
            name='Vendor',
        ),
    ]