# Generated by Django 3.2.7 on 2022-02-13 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='facebook',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='facebook'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='instagram',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='instagram'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='twitter',
            field=models.URLField(blank=True, max_length=255, null=True, verbose_name='twitter'),
        ),
    ]
