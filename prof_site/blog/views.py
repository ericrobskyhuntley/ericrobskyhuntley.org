from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views import generic
from django.core.serializers import serialize

from .models import Post, Author, UrbanArea, Land

class IndexView(generic.ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'latest_post_list'

    def get_queryset(self):
        """Return the last ten published posts."""
        return Post.objects.order_by('-timestamp')[:10]

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post_detail'

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'blog/author_detail.html'
    context_object_name = 'author_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['ua_all'] = serialize('geojson', UrbanArea.objects.all(), fields=('geom'))
        # context['land_all'] = serialize('geojson', Land.objects.all(), fields=('geom'))
        return context
