# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-09-28 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculator', '0006_auto_20180928_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simple',
            name='file_uuid',
            field=models.CharField(default=b'0000000', editable=False, max_length=50),
        ),
    ]
