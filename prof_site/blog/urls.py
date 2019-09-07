from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('author/<slug:slug>/', views.AuthorDetailView.as_view(), name='author_detail'),
]
