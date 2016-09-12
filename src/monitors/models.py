# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
import os
from django.conf import settings
import xmlrpclib

from pymongo import MongoClient

client = MongoClient()
db = client.twitter


type_list = (
    ('search', 'search'),
    ('stream', 'stream'),
)

def list_of_ids(value):
    ids = value.split(',')
    try:
        for i in ids:
            int(i.strip())
    except:
        raise ValidationError("Please enter a list of numerical IDs")

consumer_key = "etXPtVksfGyBbBdTXeaqMBziq"
consumer_secret = "SCSqatlxVEMDWAStnAgleM5r6XVmvUtuShT7tBZqcMjWK7ae6u"
access_token = "3222575935-8e42Mt1dcZcx7QTUvKAWtEB9M0lEclRMZVklznV"
access_token_secret = "3LSWpVIyrR9H5dOTaASfyVUAzjvt1J08n09djBU7Nbmr0"


class Monitor(models.Model):
    name = models.CharField(max_length=100,help_text="Select a label for your collection of tweets.")
    type = models.CharField(choices=type_list, max_length=20)
    follow = models.TextField(blank=True,null=True,help_text="A comma separated list of user IDs, indicating the users to return statuses for in the stream. More information at https://dev.twitter.com/docs/streaming-apis/parameters#follow",verbose_name="List of User IDs to follow (separated with commas)",validators=[list_of_ids])
    track = models.TextField(blank=True,null=True,help_text="A comma separated list of keywords or phrases to track. Phrases of keywords are specified by a comma-separated list. More information at https://dev.twitter.com/docs/streaming-apis/parameters#track",verbose_name="List of keywords to track (separated with commas)")
    locations = models.TextField(blank=True,null=True,help_text="A comma-separated list of longitude,latitude pairs specifying a set of bounding boxes to filter Tweets by. On geolocated Tweets falling within the requested bounding boxes will be included—unlike the Search API, the user\'s location field is not used to filter tweets. Each bounding box should be specified as a pair of longitude and latitude pairs, with the southwest corner of the bounding box coming first. For example: \"-122.75,36.8,-121.75,37.8\" will track all tweets from San Francisco. NOTE: Bounding boxes do not act as filters for other filter parameters. More information at https://dev.twitter.com/docs/streaming-apis/parameters#locations",verbose_name="List of coordinates")
    updated = models.DateTimeField(auto_now=False, auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    def start(self):
        # os.system("python tap/twitter.py %s --consumer-key %s --consumer-secret %s -q %s -v DEBUG" % (self.type, consumer_key, consumer_secret, self.track))

        # ###### via supervisor ####
        s = xmlrpclib.ServerProxy(settings.SUPERVISOR_URI)
        if not self.exists():
            try:
                if self.type == 'search':
                    s.twiddler.addProgramToGroup('tweetset', 'monitor' + str(self.name),
                                                 {'command': "python tap/twitter.py %s -ck %s -cs %s -q %s -v DEBUG" % (self.type, consumer_key, consumer_secret, self.track),
                                                  'autostart': 'true',
                                                  'autorestart': 'true',
                                                  'startsecs': '3'})
                else:
                    s.twiddler.addProgramToGroup('tweetset', 'monitor' + str(self.name),
                                                 {'command': "python tap/twitter.py %s -t %s -ck %s -cs %s -at %s -ats %s -v DEBUG" % (self.type, self.track, consumer_key, consumer_secret, access_token, access_token_secret),
                                                     'autostart': 'true',
                                                     'autorestart': 'true',
                                                     'startsecs': '3'})
            except:
                return False
        if not self.is_running():
            try:
                s.supervisor.startProcess('tweetset:monitor' + str(self.name))
            except:
                return False
            return True
        return True

    def stop(self):
        s = xmlrpclib.ServerProxy(settings.SUPERVISOR_URI)
        if self.exists():
            if self.is_running():
                s.supervisor.stopProcess('tweetset:monitor'+str(self.name))
            s.twiddler.removeProcessFromGroup('tweetset','monitor'+str(self.name))

    def exists(self):
        s = xmlrpclib.ServerProxy(settings.SUPERVISOR_URI)
        try:
            l = s.supervisor.getAllProcessInfo()
        except:
            return False
        names = [x['name'] for x in l]
        if 'monitor' + str(self.name) in names:
            return True
        else:
            return False

    def is_running(self):
        if self.exists():
            s = xmlrpclib.ServerProxy(settings.SUPERVISOR_URI)
            p_info = s.supervisor.getProcessInfo('tweetset:monitor' + str(self.name))
            if p_info['statename'] == 'RUNNING':
                return True
            else:
                return False
        else:
            return False

    def delete(self):
        self.stop()
        # querries = db.queries
        # result = querries.find({'query': self.track})
        # print result
        # id = result[0]['_id']
        # print id
        # db.queries.remove({'_id': ObjectId(id)})
        # db.tweets.remove({'_id': ObjectId(id)})
        db.queries.remove({'query': self.track})
        db.tweets.remove({'query': self.track})
        super(Monitor, self).delete()


    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['-timestamp']

# python twitter.py search -q sex -ck etXPtVksfGyBbBdTXeaqMBziq -cs SCSqatlxVEMDWAStnAgleM5r6XVmvUtuShT7tBZqcMjWK7ae6u -tc prova -v DEBUG

# python twitter.py stream -t sex -ck etXPtVksfGyBbBdTXeaqMBziq -cs SCSqatlxVEMDWAStnAgleM5r6XVmvUtuShT7tBZqcMjWK7ae6u -at 3222575935-8e42Mt1dcZcx7QTUvKAWtEB9M0lEclRMZVklznV -ats 3LSWpVIyrR9H5dOTaASfyVUAzjvt1J08n09djBU7Nbmr0
# python twitter.py stream -t "hot dog" -ck etXPtVksfGyBbBdTXeaqMBziq -cs SCSqatlxVEMDWAStnAgleM5r6XVmvUtuShT7tBZqcMjWK7ae6u -at 3222575935-8e42Mt1dcZcx7QTUvKAWtEB9M0lEclRMZVklznV -ats 3LSWpVIyrR9H5dOTaASfyVUAzjvt1J08n09djBU7Nbmr0 -tc prova -v DEBUG
