# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-12 10:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weekly', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weeklyreport',
            options={'verbose_name': '\u9031\u5831\u6578\u64da\u8868', 'verbose_name_plural': '\u9031\u5831\u6578\u64da\u8868'},
        ),
        migrations.AlterUniqueTogether(
            name='weeklyreport',
            unique_together=set([('year', 'week', 'name')]),
        ),
    ]
