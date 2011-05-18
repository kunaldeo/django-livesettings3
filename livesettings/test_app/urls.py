from django.conf.urls.defaults import *
# Imported '*' because Django 1.2 requires importing handler404+500 in the main
# urls or have customized their templates. Django 1.3 does not require it.
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^settings/', include('livesettings.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
    (r'^$', 'localsite.views.index')
)
