# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partner_feeds.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', models.ImageField(upload_to=b'img/partner-logos/', blank=True)),
                ('name', models.CharField(max_length=75)),
                ('url', models.URLField(help_text=b'Partner Website', verbose_name=b'URL')),
                ('feed_url', models.URLField(help_text=b'URL of a RSS or ATOM feed', unique=True, verbose_name=b'Feed URL')),
                ('date_feed_updated', models.DateTimeField(null=True, verbose_name=b'Feed last updated', blank=True)),
            ],
            options={
            },
            bases=(partner_feeds.models.Mixin, models.Model),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(verbose_name=b'URL')),
                ('guid', models.CharField(max_length=255, verbose_name=b'GUID')),
                ('byline', models.CharField(default=b'', max_length=255, blank=True)),
                ('date', models.DateTimeField()),
                ('image_url', models.URLField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('partner', models.ForeignKey(to='partner_feeds.Partner')),
            ],
            options={
                'ordering': ('-date',),
            },
            bases=(partner_feeds.models.Mixin, models.Model),
        ),
        migrations.CreateModel(
            name='CitiesPartnerPost',
            fields=[
            ],
            options={
                'verbose_name': 'Cities Post',
                'proxy': True,
                'verbose_name_plural': 'Cities Posts',
            },
            bases=('partner_feeds.post',),
        ),
        migrations.CreateModel(
            name='QuartzPartnerPost',
            fields=[
            ],
            options={
                'verbose_name': 'Quartz Post',
                'proxy': True,
                'verbose_name_plural': 'Quartz Posts',
            },
            bases=('partner_feeds.post',),
        ),
        migrations.CreateModel(
            name='WirePartnerPost',
            fields=[
            ],
            options={
                'verbose_name': 'Wire Post',
                'proxy': True,
                'verbose_name_plural': 'Wire Posts',
            },
            bases=('partner_feeds.post',),
        ),
    ]
