from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /analyzer
    url(r'^$', views.home, name='home'),
    # ex: /analyzer/project/nombreProyecto
    url(r'^project/(.*)', views.projectInfo, name='projectInfo'),
    # ex: /analyzer/project/nombreProyecto/nombreFichero
    url(r'^file/(.*)', views.fileInfo, name='fileInfo'),
    # ex: /analyzer/bear/BearId
    url(r'^bear/(.*)', views.bearInfo, name='bearInfo'),
    # ex: /analyzer/analyse
    url(r'^analyse/$', views.analyse, name='analyse'),
    # ex: /analyzer/analyseURL
    url(r'^analyseURL/$', views.analyseURL, name='analyseURL'),
    # ex: /analyzer/analyseFile
    url(r'^analyseFile/$', views.analyseFile, name='analyseFile'),
    # ex: /analyzer/processfile
    url(r'^processFile/$', views.processFile, name='processFile'),
    # ex: /analyzer/processurl
    url(r'^processURL/$', views.processURL, name='processURL'),
    # ex: /analyzer/search
    url(r'^search/$', views.search, name='search'),
    # ex: /analyzer/show
    url(r'^show/$', views.showResults, name='show'),
    # ex: /analyzer/statistics/bear
    url(r'^statistics/bear/$', views.statisticsBear, name='statisticsBear'),
    # ex: /analyzer/statistics/bear
    url(r'^statistics/file/$', views.statisticsFile, name='statisticsFile'),
    # ex: /analyzer/statistics/bear
    url(r'^statistics/project/$', views.statisticsProject, name='statisticsProject'),
]
