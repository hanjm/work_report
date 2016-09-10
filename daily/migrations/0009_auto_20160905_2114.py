# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-05 13:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daily', '0008_auto_20160905_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='order',
            field=models.IntegerField(help_text='\u65e5\u5831\u4e3b\u9801\u986f\u793a\u7684\u8868\u683c\u6309\u6b64\u503c\u964d\u5e8f\u6392\u5217\u7528\u6236', verbose_name='\u6392\u5e8f\u6b0a\u503c'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.OneToOneField(help_text='\u93c8\u63a5\u5230\u6388\u6b0a->\u7528\u6236\u4e2d\u7684\u7528\u6236\u540d\uff0c\u6240\u4ee5\uff0c\u6dfb\u52a0\u7528\u6236\u524d\u9700\u8981\u5148\u5230\u6388\u6b0a->\u7528\u6236\u4e2d\u6dfb\u52a0\u4e00\u500b\u53ef\u767b\u9678\u7528\u6236', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username', verbose_name='\u5de5\u865f'),
        ),
    ]