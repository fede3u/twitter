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


def simple_chart(request):
    import pandas as pd
    import numpy as np
    from bson import json_util, ObjectId
    from pandas.io.json import json_normalize
    import json

    from pandas import Series, DataFrame
    from bokeh.plotting import figure
    from bokeh.embed import components
    from math import pi
    from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper
    from bokeh.sampledata.unemployment1948 import data

    tweets = db.tweets
    dates = tweets.find({"query":"sex"},{'created_at':1})


    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)

    df['created_at.$date'] = pd.to_datetime(df['created_at.$date'], unit='ms')
    df['second'] = df['created_at.$date'].dt.second
    df['minute'] = df['created_at.$date'].dt.minute
    df.drop(df.columns[[0,1]], axis=1, inplace=True)
    final = DataFrame({'count': df.groupby(["minute", "second"]).size()}).reset_index()
    d = DataFrame(final.pivot(index='minute', columns='second', values='count').reset_index())
    d.fillna(0, inplace=True)
    print d

    # data['Year'] = [str(x) for x in data['Year']]
    d['minute'] = [str(x) for x in d['minute']]
    d.columns = [str(x) for x in d.columns]


    # years = list(data['Year'])
    years = list(d['minute'])

    # months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months = d.columns.tolist()[1:]

    # data = data.set_index('Year')
    data = d.set_index('minute')


    # this is the colormap from the original NYTimes plot
    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    mapper = LinearColorMapper(palette=colors)
    # Set up the data for plotting. We will need to have values for every
    # pair of year/month names. Map the rate to a color.
    month = []
    year = []
    color = []
    rate = []
    for y in years:
        for m in months:
            month.append(m)
            year.append(y)
            monthly_rate = data[m][y]
            rate.append(monthly_rate)

    source = ColumnDataSource(
        data=dict(month=month, year=year, rate=rate)
    )

    TOOLS = "hover,save,pan,box_zoom,wheel_zoom"

    p = figure(title="Sex world usage on twitter by minute",
               x_range=years, y_range=list(reversed(months)),
               x_axis_location="above", plot_width=900, plot_height=400,
               tools=TOOLS)

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = pi / 3

    p.rect(x="year", y="month", width=1, height=1,
           source=source,
           fill_color={'field': 'rate', 'transform': mapper},
           line_color=None)

    p.select_one(HoverTool).tooltips = [
        ('second', '@month'),
        ('minute', '@year'),
        ('rate', '@rate'),
    ]

    # show the results
    # show(p)
    #
    # plot = figure()
    # plot.circle([1,2], [3,4])
    script, div = components(p)

    context = {"the_script": script, "the_div": div}
    template = "simple_chart.html"
    return render(request, template, context)