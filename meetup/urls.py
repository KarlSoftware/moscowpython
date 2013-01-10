# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from .views import EventPage, TalkPage, SpeakerPage, SpeakerList, IndexPage, EventsList, AboutPage, LivePage, ajax_subscribe


urlpatterns = patterns('',
    url('^$', IndexPage.as_view(), name='index'),
    url('^subscribe/$', ajax_subscribe, name='subscribe'),
    url('^about/$', AboutPage.as_view(), name='about'),
    url('^live/$', LivePage.as_view(), name='live'),
    url('^meetup/$', EventsList.as_view(), name='events'),
    url('^meetup/(?P<number>\d+)/$', EventPage.as_view(), name='event'),
    url('^meetup/(?P<event_number>\d+)/(?P<talk_slug>[\w-]+)/$', TalkPage.as_view(), name='talk'),
    url('^speakers/$', SpeakerList.as_view(), name='speakers'),
    url('^speakers/(?P<slug>[\w-]+)/$', SpeakerPage.as_view(), name='speaker'),
    url('', include('meetup.legacy.urls')),
)
