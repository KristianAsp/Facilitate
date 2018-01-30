from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth.views import logout

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_index, name="user_login"),
    url(r'^register/$', views.register_index, name ="register_index"),
    url(r'^dashboard/$', views.dashboard_index),
    url(r'^profile/$', views.profile_index),
    url(r'^settings/$', views.settings_index),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^project/new/$', views.new_project, name='new_project'),
    url(r'^dashboard/(?P<pk>[0-9]+)$', views.dashboard_project_view, name = 'project_index'),
    url(r'^dashboard/tasks/$', views.dashboard_ticket_view,  name = 'dashboard_ticket_view'),
    url(r'^dashboard/tasks/new$', views.new_ticket_view,  name = 'new_ticket_view'),
    url(r'^project/settings$', views.new_ticket_view,  name = 'project_settings'),
]
