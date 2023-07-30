from django.conf.urls import url
from livesettings import views

urlpatterns = [
    url(r'^$', views.site_settings, name='satchmo_site_settings'),
    url(r'^export/$', views.export_as_python, name='settings_export'),
    url(r'^(?P<group>[^/]+)/$', views.group_settings, name='livesettings_group'),
]
