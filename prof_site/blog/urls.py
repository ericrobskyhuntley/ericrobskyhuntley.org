from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('person/<slug:slug>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('api/vita/', views.vita_view, name='vita_json'),
]
