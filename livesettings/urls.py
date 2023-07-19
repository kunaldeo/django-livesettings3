try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from livesettings import views

urlpatterns = [
    re_path(r'^$', views.site_settings, name='satchmo_site_settings'),
    re_path(r'^export/$', views.export_as_python, name='settings_export'),
    re_path(r'^(?P<group>[^/]+)/$', views.group_settings, name='livesettings_group'),
]
