from django.conf.urls import *
from django.contrib import admin

urlpatterns = patterns('',
    (r'^settings/', include('livesettings.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
)
