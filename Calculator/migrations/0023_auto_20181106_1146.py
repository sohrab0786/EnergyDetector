# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-06 06:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculator', '0022_auto_20181104_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='simple',
            name='cool_save',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='cool_save_area',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='cool_save_cost',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='heat_save',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='heat_save_area',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='heat_save_cost',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='total_save',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='total_save_area',
            field=models.CharField(default=b'x', max_length=50),
        ),
        migrations.AddField(
            model_name='simple',
            name='total_save_cost',
            field=models.CharField(default=b'x', max_length=50),
        ),
    ]
