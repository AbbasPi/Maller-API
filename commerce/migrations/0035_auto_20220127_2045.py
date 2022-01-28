# Generated by Django 3.2.8 on 2022-01-27 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0034_auto_20220127_2041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_rating',
        ),
        migrations.AddField(
            model_name='productrating',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='commerce.product'),
        ),
        migrations.AlterField(
            model_name='productrating',
            name='rate',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]