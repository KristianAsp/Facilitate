from django.conf.urls import url, include
from django.contrib import admin
from .models import Project
from . import api_views, auth_login
from rest_framework.authtoken import views
from .serializers import serializers
from rest_framework import routers, viewsets

urlpatterns = [
    url(r'^projects/$', api_views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', api_views.ProjectDetail.as_view()),
    url(r'^users/$', api_views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', api_views.UserDetail.as_view()),
    url(r'^api-token-auth/', views.obtain_auth_token), ##Obtains the valid API Token when a POST request is sent with a valid username and password (hashed)
]
