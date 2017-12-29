from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_index, name="user_login"),
    url(r'^register/$', views.register_index, name ="register_index"),
    url(r'^dashboard/$', views.dashboard_index),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^project/new/$', views.new_project, name='new_project'),
    url(r'^dashboard/display/$', views.display_tickets, name = 'display_tickets')
]
