from pymongo import MongoClient
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
from bokeh.charts import Line, Donut

from gviz_data_table import Table


client = MongoClient()
db = client.twitter


def heatmap(query):

    tweets = db.tweets
    # dates = tweets.find({"query":"sex"},{'created_at':1})
    pipeline = [{'$match': {'query': query}}, {'$sample': {'size': 1000}}, {'$project': {'created_at': 1}}]
    dates = tweets.aggregate(pipeline)
    dates = dates['result']

    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)
    # print df

    df['created_at.$date'] = pd.to_datetime(df['created_at.$date'], unit='ms')
    df['second'] = df['created_at.$date'].dt.second
    df['day'] = df['created_at.$date'].dt.dayofweek
    df['hour'] = df['created_at.$date'].dt.hour
    df['minute'] = df['created_at.$date'].dt.minute
    # print df
    df.drop(df.columns[[0, 1]], axis=1, inplace=True)
    final = DataFrame({'count': df.groupby(["minute", "second"]).size()}).reset_index()
    d = DataFrame(final.pivot(index='minute', columns='second', values='count').reset_index())
    d.fillna(0, inplace=True)
    # print d

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

    p = figure(x_range=years, y_range=list(reversed(months)),
               x_axis_location="above", plot_width=500, plot_height=400,
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

    script, div = components(p)
    return script, div


def line_chart(query):
    tweets = db.tweets
    # dates = tweets.find({"query":"sex"},{'created_at':1})
    # dates = tweets.aggregate({"$sample": {"size":100}})
    # print dates
    pipeline = [{'$match': {'query': query}}, {'$sample': {'size': 1000}}, {'$project': {'created_at': 1}}]
    dates = tweets.aggregate(pipeline)
    dates = dates['result']
    # dates = tweets.find({"query":"sex"},{'created_at':1})


    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)
    # print df

    df['created_at.$date'] = pd.to_datetime(df['created_at.$date'], unit='ms')
    df['second'] = df['created_at.$date'].dt.second
    df['day'] = df['created_at.$date'].dt.dayofweek
    df['hour'] = df['created_at.$date'].dt.hour
    df['minute'] = df['created_at.$date'].dt.minute
    df.drop(df.columns[[0, 1]], axis=1, inplace=True)
    d = DataFrame({'count': df.groupby(["minute"]).size()}).reset_index()
    # d = DataFrame(final.pivot(index='minute', columns='second', values='count').reset_index())
    d.fillna(0, inplace=True)
    # print d

    name = [str(x) for x in d['minute']]
    numbers = d['count']

    # build a dataset where multiple columns measure the same thing
    data = dict(numbers=numbers, name=name)

    # create a line chart where each column of measures receives a unique color and dash style
    p = Line(data, y=['numbers'],
             dash=['numbers'],
             color=['numbers'],
             legend_sort_field='color',
             legend_sort_direction='ascending',
             ylabel='Frequency',
             xlabel='Timeframe',
             legend=False,
             plot_width=500,
             plot_height=400,)

    script, div = components(p)
    return script, div

def pie(query):
    ##### data from twitter #####
    tweets = db.tweets
    pipeline = [{'$match': {'query': query}}, {'$sample': {'size': 1000}},
                {'$project': {'user.lang': 1, 'user.time_zone': 1}}]
    dates = tweets.aggregate(pipeline)
    dates = dates['result']
    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)

    d = DataFrame({'count': df.groupby(["user.lang", "user.time_zone"]).size()}).reset_index()
    d = DataFrame(d.pivot(index='user.lang', columns='user.time_zone', values='count').reset_index())
    d.fillna(0, inplace=True)

    d = pd.melt(d, id_vars=['user.lang'],
                value_vars=list(d.columns.values)[1:],
                value_name='count', var_name='t_count')
    d = d[d['count'] > 1]
    d['count'] = [int(x) for x in d['count']]
    d.reset_index(inplace=True)
    del d['index']
    # print d

    #
    # df = pd.melt(df, id_vars=['abbr'],
    #              value_vars=['bronze', 'silver', 'gold'],
    #              value_name='medal_count', var_name='medal')
    # print df

    p = Donut(d, label=['user.lang'])

    script, div = components(p)
    return script, div

def usmap(query):
    tweets = db.tweets
    pipeline = [{'$match': {'query': query, 'place.country_code': 'US'}}, {'$project': {'place.full_name': 1}}]
    dates = tweets.aggregate(pipeline)
    dates = dates['result']
    sanitized = json.loads(json_util.dumps(dates))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)

    df = DataFrame({'count': df.groupby(["place.full_name"]).size()}).reset_index()

    table = Table()
    table.add_column('place', str, 'place.full_name')
    table.add_column('count', int, 'count')

    for row in df.iterrows():
        a = row[1].tolist()
        a[0] = a[0].encode()
        table.append(a)
    table = table.encode()
    table = json.dumps(table)

    return table


def word_cloud(query):
    tweets = db.tweets
    pipeline = [
    {'$match': {'query': query}},
    {'$unwind': '$entities.hashtags'},
    {'$group': {
        '_id' : '$entities.hashtags.text',
        'tagCount': {'$sum': 1}
    }},
    {'$sort': {
        'tagCount': -1
    }},
    {'$limit':50},
    {'$project': {
        'name':'$_id',
        'tagCount':1}}
    ]
    tags = tweets.aggregate(pipeline)
    tags = tags['result']

    sanitized = json.loads(json_util.dumps(tags))
    normalize = json_normalize(sanitized)
    df = pd.DataFrame(normalize)
    dt = pd.cut(df['tagCount'],5,labels=[1,2,3,4,5])

    df['size'] = dt
    df = df.sort(columns='name')
    df = df.to_dict('records')
    return df

def avg_quadrant(query):
    tweets = db.tweets
    count = tweets.find({"query": query}).count()
    list = tweets.find({'$query':{'query':query},'$orderby':{'$natural':-1}}).limit(100)
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
    return avg, count, list
