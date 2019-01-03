# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-02 21:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=140)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('source_comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='comment.Comment')),
                ('target_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
