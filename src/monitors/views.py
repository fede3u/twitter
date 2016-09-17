from django.shortcuts import render, get_object_or_404

from pymongo import MongoClient
from charts import heatmap, line_chart, pie, usmap, word_cloud, avg_quadrant
from bson.objectid import ObjectId


client = MongoClient()
db = client.twitter

def Monitor_list(request):
    querries = db.queries
    result = querries.find({})
    instance = []
    for x in result:
        instance.append({'id':x['_id'],'query':x['monitor_name']})
    print instance
    context = {"instance": instance}
    template = "monitor_list.html"
    return render(request, template, context)


def Monitor_detail(request,id):
    querries = db.queries
    result = querries.find({'_id': ObjectId(id)})
    query = result[0]['query']

    script_hm, div_hm = heatmap(query)
    script_lc, div_lc = line_chart(query)
    # script_pie, div_pie = pie(query)
    table = usmap(query)
    tags = word_cloud(query)
    avg, count, list = avg_quadrant(query)

    context = {"list": list,
               "count": count,
               "query": query,
               "script_hm": script_hm,
               "script_lc": script_lc,
               # "script_pie":script_pie,
               "div_hm": div_hm,
               "div_lc": div_lc,
               # "div_pie":div_pie,
               "avg" : avg,
               "table": table,
               "tags": tags}
    template = "monitor_detail.html"
    return render(request, template, context)


def simple_chart(request):

    context = {'tags': "df"}
    template = "google_chart.html"
    return render(request, template, context)
