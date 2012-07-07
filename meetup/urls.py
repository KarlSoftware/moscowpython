# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView
from meetup.views import EventPage, TalkPage
from views import IndexPage

urlpatterns = patterns('',
    url('^$', IndexPage.as_view(), name='index'),
    url('^meetups/$', EventPage.as_view(), name='events'),
    url('^meetups/(?P<pk>\d+)/$', EventPage.as_view(), name='event'),
    url('^meetups/(?P<event_id>\d+)/(?P<talk_slug>[\w-]+)/$', TalkPage.as_view(), name='talk'),
)