from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from django.core.serializers import serialize
from el_pagination.decorators import page_template

from .models import Post, Person, UrbanArea, Land, Event

from el_pagination.views import AjaxListView

class IndexView(AjaxListView):
    context_object_name = 'latest_post_list'
    template_name = 'blog/post_list.html'
    page_template = 'blog/post_list_page.html'

    def get_queryset(self):
        """Return the last ten published posts."""
        return Post.objects.order_by('-timestamp')[1:]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['first'] = Post.objects.order_by('-timestamp')[0]
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ua_all'] = serialize('geojson', 
            UrbanArea.objects.all(),
            fields=('geom')
        )
        context['land_all'] = serialize('geojson', 
            Land.objects.all(), 
            fields=('geom')
        )
        # context['bath_all'] = serialize(
        #     'geojson', 
        #     BathContours.objects.all(),
        #     fields=('geom')
        # )
        # context['elev_all'] = serialize(
        #     'geojson',
        #     ElevContours.objects.all(),
        #     fields=('geom')
        # )
        return context
