from django.conf.urls import url, include
from . import views


urlpatterns = [
    url(r'^$', views.Monitor_list, name='list'),
    url(r'^simple_chart/$', views.simple_chart, name="simple_chart"),
    url(r'^(?P<id>[a-z0-9-]+)/$', views.Monitor_detail, name='detail'),
]
