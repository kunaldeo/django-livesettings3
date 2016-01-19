from django.conf.urls import patterns, url

urlpatterns = patterns('livesettings.views',
    url(r'^$', 'site_settings', name='satchmo_site_settings'),
    url(r'^export/$', 'export_as_python', name='settings_export'),
    url(r'^(?P<group>[^/]+)/$', 'group_settings', name='livesettings_group'),
)
