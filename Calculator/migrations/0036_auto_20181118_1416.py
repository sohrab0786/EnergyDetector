# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-18 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculator', '0035_auto_20181117_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='detailed_data',
            name='username',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='parametric_data',
            name='username',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
