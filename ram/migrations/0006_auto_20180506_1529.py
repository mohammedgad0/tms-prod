# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-06 12:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ram', '0005_auto_20180506_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answers',
            name='answer_no',
            field=models.CharField(db_column='ANSWER_NO', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='answers',
            unique_together=set([]),
        ),
    ]
