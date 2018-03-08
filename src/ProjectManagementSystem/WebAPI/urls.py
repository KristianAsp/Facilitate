from django.conf.urls import url, include
from django.contrib import admin
from .models import Project
from . import api_views, auth_login
from rest_framework.authtoken import views as rest_framework_views
from .serializers import serializers
from rest_framework import routers, viewsets

urlpatterns = [
    url(r'^projects/$', api_views.ProjectList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/$', api_views.ProjectDetail.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/users/$', api_views.ProjectUsersList.as_view()),
    url(r'^projects/(?P<pk>[0-9]+)/users/all$', api_views.ProjectUsers.as_view()),
    url(r'^users/$', api_views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', api_views.UserDetail.as_view()),
    url(r'^users/(?P<email>[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4})/$', api_views.UserDetailEmail.as_view()),
    url(r'^users/(?P<slug>[\w_-]+)/$', api_views.UserDetailUsername.as_view()),
    url(r'^profiles/$', api_views.ProfileList.as_view()),
    url(r'^profiles/(?P<pk>[0-9]+)/$', api_views.ProfileDetail.as_view()),
    url(r'^profiles/(?P<email>[a-zA-Z0-9._%+-@]+)/$', api_views.ProfileDetailEmail.as_view()),
    url(r'^account/login/$', api_views.LoginUser.as_view()),
    url(r'^account/logout/$', api_views.LogoutUser.as_view()),
    url(r'^account/authenticate/$', api_views.AuthenticateUser.as_view()),
    url(r'^tickets/(?P<pk>[0-9]+)/$', api_views.TicketDetail.as_view(), name = 'display_tickets'),
    url(r'^projects/(?P<pk>[0-9]+)/tickets/$', api_views.TicketList.as_view(), name = 'display_tickets'),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name = 'get_auth_token'), ##Obtains the valid API Token when a POST request is sent with a valid username and password (hashed)
]
