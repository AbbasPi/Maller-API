# Generated by Django 3.2.8 on 2022-01-24 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commerce', '0024_auto_20220124_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrating',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='vendorrating',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_rating', to=settings.AUTH_USER_MODEL),
        ),
    ]