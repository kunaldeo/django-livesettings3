from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/settings/$', include('livesettings.urls')),
)
