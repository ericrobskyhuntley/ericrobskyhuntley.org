from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from el_pagination.decorators import page_template
from django.db.models import F
from .models import SiteWideSetting, Post, Person, UrbanArea, Land, Event, Education, Affiliation, Award
from django.http import HttpResponse, JsonResponse
from .serializers import EducationSerializer, InstitutionSerializer, MainPersonSerializer, AffiliationSerializer, AwardSerializer

from datetime import datetime, timedelta, time
from el_pagination.views import AjaxListView

def vita_view(request):
    try:
        main_person_id = SiteWideSetting.objects.all()[0].main_person.id
        main_person = Person.objects.filter(
                id=main_person_id
            ).all()
        education = Education.objects.filter(
                show=True,
                person__id=main_person_id
            ).order_by(
                F('end').desc(nulls_first=True)
            )
        appointments = Affiliation.objects.filter(
                person__id=main_person_id,
                show=True,
                kind='App',
            ).order_by(
                F('primary').desc(),
                F('end').desc(nulls_first=True),
            )
        affiliations = Affiliation.objects.filter(
                person__id=main_person_id,
                show=True,
                kind='Aff',
                end=None
            ).order_by(
                F('end').desc(nulls_first=True)
            )
        funding = Award.objects.filter(
                pi_awardee__id=main_person_id,
                show=True,
                kind='F'
            ).order_by(F('start').desc(nulls_first=True))
        awards = Award.objects.filter(
                pi_awardee__id=main_person_id,
                show=True,
                kind='A'
            ).order_by(F('start').desc(nulls_first=True))
        advisees = Education.objects.filter(
                committee__id__exact=main_person_id
            ).order_by(
                F('end').desc(nulls_first=True)
            )
    except Education.DoesNotExist or Person.DoesNotExist or Affiliation.DoesNotExist or Award.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        main_s = MainPersonSerializer(main_person, many=True)
        appointments_s = AffiliationSerializer(appointments, many=True)
        education_s = EducationSerializer(education, many=True)
        affiliations_s = AffiliationSerializer(affiliations, many=True)
        funding_s = AwardSerializer(funding, many=True)
        awards_s = AwardSerializer(awards, many=True)
        advisees_s = EducationSerializer(advisees, many=True)
        return JsonResponse({
            'main': main_s.data[0],
            'appointments': appointments_s.data,
            'education': education_s.data,
            'affiliations': affiliations_s.data,
            'funding': funding_s.data,
            'awards': awards_s.data,
            'advisees': advisees_s.data
            }, safe=False)

class IndexView(AjaxListView):
    context_object_name = 'latest_post_list'
    template_name = 'blog/post_list.html'
    page_template = 'blog/post_list_page.html'

    def get_queryset(self):
        """Return the last ten published posts."""
        return Post.objects.order_by('-display_datetime')[1:]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['first'] = Post.objects.order_by('-display_datetime')[0]
        context['events'] = Event.objects.order_by('day')
        return context

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post_detail'

class PersonDetailView(generic.DetailView):
    model = Person
    template_name = 'blog/person_detail.html'
    context_object_name = 'person_detail'