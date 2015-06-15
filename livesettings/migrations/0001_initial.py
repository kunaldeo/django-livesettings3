# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import keyedcache.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LongSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('value', models.TextField(blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            bases=(models.Model, keyedcache.models.CachedObjectMixin),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255, blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            bases=(models.Model, keyedcache.models.CachedObjectMixin),
        ),
        migrations.AlterUniqueTogether(
            name='setting',
            unique_together=set([('site', 'group', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='longsetting',
            unique_together=set([('site', 'group', 'key')]),
        ),
    ]
