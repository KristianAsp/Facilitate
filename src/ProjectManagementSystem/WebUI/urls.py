from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth.views import logout

handler404 = views.handler404

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_index, name="user_login"),
    url(r'^register/$', views.register_index, name ="register_index"),
    url(r'^forgot/$', views.forgotten_password, name="forgotten_password"),
    url(r'^reset/(?P<slug>[\w]+)/$', views.reset_password, name="reset_password"),
    url(r'^dashboard/$', views.dashboard_index),
    url(r'^profile/$', views.profile_index),
    url(r'^settings/$', views.settings_index, name='user_settings'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'^project/new/$', views.new_project, name='new_project'),
    url(r'^dashboard/(?P<pk>[0-9]+)$', views.dashboard_project_view, name = 'project_index'),
    url(r'^dashboard/delete/(?P<pk>[0-9]+)/(?P<slug>[\w_-]+)/$', views.delete_state, name = 'delete_state'),
    url(r'^dashboard/tasks/$', views.dashboard_ticket_view,  name = 'dashboard_ticket_view'),
    url(r'^dashboard/tasks/new$', views.new_ticket_view,  name = 'new_ticket_view'),
    url(r'^project/settings$', views.project_settings_view,  name = 'project_settings'),
    url(r'^project/settings/users$', views.user_project_settings, name = 'user_project_settings'),
    url(r'^project/users/delete/(?P<slug>[\w_-]+)/$', views.remove_user_from_project, name = 'remove_user_from_project'),
    url(r'^project/delete$', views.delete_project, name = 'delete_project'),
    url(r'^project/tickets/detail/(?P<slug>[ \w_-]+)/$', views.ticket_detail, name = 'ticket_detail'),
    url(r'^project/tickets/changes/$', views.project_ticket_changes, name = 'project_ticket_changes'),
    url(r'^(?P<slug>[\w_-]+)/$', views.view_user_profile, name = 'view_user_profile'),
    url(r'^search$', views.search, name = "search"),
    url(r'^dashboard/board/(?P<pk>[0-9]+)$', views.update_board_display, name='update_board_display'),
    url(r'^dashboard/board/new$', views.new_board, name='new_board'),
    url(r'^dashboard/board/delete$', views.delete_board, name='delete_board'),
    url(r'^profile/update/$', views.updateUserDetails, name='updateUserDetails'),
    url(r'^profile/update/password$', views.updateUserPassword, name='updateUserPassword'),

]
