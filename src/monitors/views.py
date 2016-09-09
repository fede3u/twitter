from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Monitor
from pymongo import MongoClient

client = MongoClient()
db = client.twitter

def Monitor_list(request):
    querries = db.queries
    instance = querries.find({})
    context = {"instance": instance}
    template = "monitor_list.html"
    return render(request, template, context)

def Monitor_detail(request, query):
    tweets = db.tweets
    count = tweets.find({"query":query}).count()
    instance = tweets.find({"query":query}).limit(100)
    context = {"instance": instance,"count": count, "query": query}
    template = "monitor_detail.html"
    return render(request, template, context)


# tweets = db.tweets
# instance = tweets.count()
# context = {"instance": instance}
# template = "monitor_list.html"
# return render(request, template, context)
