from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth.views import logout
urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_index, name="user_login"),
    url(r'^register/$', views.register_index),
    url(r'^dashboard/$', views.dashboard_index),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^register/process_register$', views.user_register, name="user_register"),
]
