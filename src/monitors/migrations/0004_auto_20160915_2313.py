# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-15 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0003_auto_20160915_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='language',
            field=models.CharField(blank=True, default='', help_text='Select a language find codes at http://www.andiamo.co.uk/resources/iso-language-codes ', max_length=100),
        ),
        migrations.AlterField(
            model_name='monitor',
            name='locations',
            field=models.TextField(blank=True, default='', help_text='A comma-separated list of longitude,latitude pairs specifying a set of bounding boxes to filter Tweets by. On geolocated Tweets falling within the requested bounding boxes will be included\u2014unlike the Search API, the user\'s location field is not used to filter tweets. Each bounding box should be specified as a pair of longitude and latitude pairs, with the southwest corner of the bounding box coming first. For example: "-122.75,36.8,-121.75,37.8" will track all tweets from San Francisco. NOTE: Bounding boxes do not act as filters for other filter parameters. More information at https://dev.twitter.com/docs/streaming-apis/parameters#locations', null=True, verbose_name='List of coordinates'),
        ),
        migrations.AlterField(
            model_name='monitor',
            name='result_type',
            field=models.CharField(blank=True, choices=[('popular', 'popular'), ('recent', 'recent'), ('mix', 'mix')], default='', help_text='You cna chose a specific type of result generated by twitter', max_length=20),
        ),
    ]
