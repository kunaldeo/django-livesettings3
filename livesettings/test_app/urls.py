from django.conf.urls.defaults import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^settings/', include('livesettings.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    (r'^$', 'localsite.views.index')
)
