from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Monitor
from pymongo import MongoClient
from charts import heatmap, line_chart, pie

client = MongoClient()
db = client.twitter

def Monitor_list(request):
    querries = db.queries
    instance = querries.find({})
    context = {"instance": instance}
    template = "monitor_list.html"
    return render(request, template, context)

# def Monitor_detail(request, query):
#     tweets = db.tweets
#     count = tweets.find({"query":query}).count()
#     instance = tweets.find({"query":query}).limit(100)
#     context = {"instance": instance,"count": count, "query": query}
#     template = "monitor_detail.html"
#     return render(request, template, context)

def Monitor_detail(request,query):
    script_hm, div_hm = heatmap(query)
    script_lc, div_lc = line_chart(query)
    script_pie, div_pie = pie(query)

    tweets = db.tweets
    count = tweets.find({"query": query}).count()
    list = tweets.find({"query":query}).limit(100)
    mugs = list
    pipeline = [
        {'$match':{'query':query}},
        {'$sample': {'size':1000}},
        {'$group': { "_id": "null",
                     'avg_foc':{'$avg':'$user.followers_count'},
                     'avg_frc':{'$avg':'$user.friends_count'},
                     'avg_sc' :{'$avg':'$user.statuses_count'},
                     'avg_rc':{'$avg':'$retweet_count'}
                     }},
        {'$project':{'avg_foc':1,'avg_frc':1, 'avg_sc': 1, 'avg_rc': 1 }}]
    avg_followers = tweets.aggregate(pipeline)
    avg = avg_followers['result'][0]
    print avg['avg_rc']

    context = {"list": list,
               "mugs": mugs,
               "count": count,
               "query": query,
               "script_hm": script_hm,
               "script_lc": script_lc,
               "script_pie":script_pie,
               "div_hm": div_hm,
               "div_lc": div_lc,
               "div_pie":div_pie,
               "avg" : avg}
    template = "monitor_detail.html"
    return render(request, template, context)


def simple_chart(request):
    # pandas and numpy imports
    import pandas as pd
    import numpy as np
    from bson import json_util, ObjectId
    from pandas.io.json import json_normalize
    import json
    from pandas import Series, DataFrame

    # bokeh related import
    from bokeh.embed import components


    ##### data from twitter #####
    tweets = db.tweets
    pipeline = [{'$match':{'query':'sex'}},{'$sample': {'size':1000}}, {'$project':{'user.lang': 1, 'user.time_zone': 1}}]
    dates = tweets.aggregate(pipeline)
    dates = dates['result']
    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)

    # df['created_at.$date'] = pd.to_datetime(df['created_at.$date'], unit='ms')
    # df['second'] = df['created_at.$date'].dt.second
    # df['day'] = df['created_at.$date'].dt.dayofweek
    # df['hour'] = df['created_at.$date'].dt.hour
    # df['minute'] = df['created_at.$date'].dt.minute
    # df.drop(df.columns[[0,1]], axis=1, inplace=True)
    d = DataFrame({'count': df.groupby(["user.lang","user.time_zone"]).size()}).reset_index()
    d = DataFrame(d.pivot(index='user.lang', columns='user.time_zone', values='count').reset_index())
    d.fillna(0, inplace=True)
    d = pd.melt(d, id_vars=['user.lang'],
               value_vars = list(d.columns.values)[1:],
               value_name ='count', var_name='t_count')
    d = d[d['count']>1]
    d['count'] = [int(x) for x in d['count']]
    d.reset_index(inplace=True)
    del d['index']
    print d


    ##### new chart  #####




    #### pass over function ####
    script, div = components(p)


    context = {"the_script": script, "the_div": div}
    template = "simple_chart.html"
    return render(request, template, context)

