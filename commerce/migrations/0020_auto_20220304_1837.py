# Generated by Django 3.2.12 on 2022-03-04 18:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0019_auto_20220304_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
