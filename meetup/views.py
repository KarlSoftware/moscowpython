import django
import sys
from django.core.urlresolvers import reverse
from django.db import DatabaseError
from django.db.models import Count

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import six
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Talk, Photo, Speaker, Event, Tutorial, Vote
from .utils import subscribe_mail, validate_email


class IndexPage(ListView):
    template_name = 'index.html'
    context_object_name = 'events'
    queryset = Event.archived.prefetch_related('talks', 'talks__speaker', 'talks__event')

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)

        context.update({
            'main_event': Event.spotlight(),
        })
        return context


class EventsList(ListView):
    template_name = 'event_list.html'
    queryset = Event.visible.prefetch_related('talks', 'talks__speaker', 'talks__event')
    context_object_name = 'events'


class EventPage(DetailView):
    template_name = 'event.html'
    slug_url_kwarg = 'number'
    slug_field = 'number'
    queryset = Event.visible.all()

    def get_context_data(self, **kwargs):
        context = super(EventPage, self).get_context_data(**kwargs)
        context.update({
            'photos': context['event'].photos.all()
        })
        return context


class TalkPage(DetailView):
    template_name = 'talk.html'
    slug_url_kwarg = 'talk_slug'
    queryset = Talk.active.select_related('event', 'speaker')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Redirect for non-canonic urls (meetup.legacy.urls)
        if self.object.get_absolute_url() != request.path:
            return redirect(self.object)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class SpeakerList(ListView):
    template_name = 'speakers.html'
    queryset = Speaker.objects.all().order_by('name')
    context_object_name = 'speakers'


class SpeakerPage(DetailView):
    template_name = 'speaker.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Speaker.objects.prefetch_related('talks', 'talks__event'),
            slug=self.kwargs['slug']
        )


class AboutPage(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutPage, self).get_context_data(**kwargs)
        context.update({
            'photos': Photo.objects.all().order_by('-pk')[:10]
        })
        return context


class LivePage(TemplateView):
    template_name = 'live.html'

    def get_context_data(self, **kwargs):
        context = super(LivePage, self).get_context_data(**kwargs)

        context.update({
            'event': Event.spotlight(),
        })
        return context


class TutorialList(ListView):
    template_name = 'tutorials.html'
    queryset = Tutorial.objects.all().order_by('title')
    context_object_name = 'tutorials'


class TutorialPage(DetailView):
    template_name = 'tutorial.html'
    model = Tutorial


class Py3Page(TemplateView):
    template_name = 'py3.html'

    def get_context_data(self, **kwargs):
        context = super(Py3Page, self).get_context_data(**kwargs)

        context.update({
            'django': django.get_version(),
            'python': sys.version,
            'py3': six.PY3,
        })
        return context


class VoteResults(TemplateView):
    template_name = 'vote_results.html'

    def get_context_data(self, **kwargs):
        context = super(VoteResults, self).get_context_data(**kwargs)
        context.update({
            'values': Talk.objects.filter(event=Event.spotlight())
                                  .annotate(num_votes=Count("votes")).values_list('name', 'num_votes'),
        })
        return context


def ajax_subscribe(request):
    if "email" in request.POST:
        email = request.POST['email']
        if validate_email(email) and subscribe_mail(email):
            return HttpResponse('OK')
    return HttpResponse('Failed')


def ajax_vote(request, *args, **kwargs):
    cookie_name = 'moscowdjango_vote'
    if request.method == 'POST':
        if request.COOKIES.get(cookie_name, None):
            return HttpResponse('Only one vote, man', status=409)
        try:
            event = Talk.objects.get(pk=kwargs['talk_id']).event
            if not event.votable:
                return HttpResponse('Voting is closed, sorry', status=409)
            Vote.objects.create(talk_id=kwargs['talk_id'],
                                event=event,
                                ua=request.META.get('HTTP_USER_AGENT'),
                                ip=request.META.get('REMOTE_ADDR'))
            response = HttpResponse(reverse('vote-results'))
            response.set_cookie(cookie_name, 'done')
            return response
        except DatabaseError:
            return HttpResponse('DB error, sorry', status=402)
    return HttpResponse('Only POST', status=402)
