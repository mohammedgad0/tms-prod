# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-07 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
        ('ram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conditions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_agree', models.NullBooleanField(db_column='IS_SUBMITTED')),
                ('emp_id', models.ForeignKey(blank=True, db_column='EMP_ID', null=True, on_delete=django.db.models.deletion.CASCADE, to='project.Employee', to_field='empid')),
            ],
            options={
                'db_table': 'RAM_CONDITIONS',
                'managed': True,
            },
        ),
    ]
