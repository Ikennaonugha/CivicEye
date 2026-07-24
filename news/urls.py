from django.urls import path
from . import views

urlpatterns = [
    path('', views.gov_news_feed, name='news_feed'),
]