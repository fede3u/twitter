# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-16 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import monitors.models


class Migration(migrations.Migration):

    dependencies = [
        ('monitors', '0011_auto_20160916_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='follow',
            field=models.TextField(blank=True, help_text='Works only for Stream API ... A comma separated list of user IDs,\n indicating the users to return statuses for in the stream. More information at https://dev.twitter.com/docs/streaming-apis/parameters#follow', null=True, validators=[monitors.models.list_of_ids], verbose_name='List of User IDs to follow (separated with commas)'),
        ),
        migrations.AlterField(
            model_name='monitor',
            name='locations',
            field=models.TextField(blank=True, default=None, help_text='A comma-separated list of longitude,latitude pairs specifying a set of bounding boxes to filter Tweets by. On geolocated Tweets falling within the requested bounding boxes will be included\u2014unlike the Search API, the user\'s location field is not used to filter tweets. Each bounding box should be specified as a pair of longitude and latitude pairs, with the southwest corner of the bounding box coming first. For example: "37.781157,-122.398720,10mi" will track all tweets from San Francisco. NOTE: Bounding boxes do not act as filters for other filter parameters. More information at https://dev.twitter.com/docs/streaming-apis/parameters#locations', verbose_name='List of coordinates'),
        ),
        migrations.AlterField(
            model_name='monitor',
            name='result_type',
            field=models.CharField(blank=True, choices=[('recent', 'recent'), ('mixed', 'mixed')], default='mixed', help_text='You cna chose a specific type of result generated by twitter', max_length=20),
        ),
    ]
