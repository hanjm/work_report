# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-08 08:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daily', '0009_auto_20160905_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.OneToOneField(help_text='\u93c8\u63a5\u5230\u6388\u6b0a->\u7528\u6236\u4e2d\u7684\u7528\u6236\u540d\uff0c\u6240\u4ee5\uff0c\u6dfb\u52a0\u7528\u6236\u524d\u9700\u8981\u5148\u6dfb\u52a0\u4e00\u500b\u53ef\u767b\u9678\u7528\u6236', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username', verbose_name='\u5de5\u865f'),
        ),
    ]
