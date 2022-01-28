# Generated by Django 3.2.8 on 2022-01-27 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0050_alter_productrating_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='An',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arbar', models.FloatField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arb', to='commerce.product')),
            ],
        ),
    ]
