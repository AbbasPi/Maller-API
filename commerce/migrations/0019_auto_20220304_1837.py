# Generated by Django 3.2.12 on 2022-03-04 18:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0018_alter_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
