# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-16 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculator', '0030_simple_result_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simple',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
