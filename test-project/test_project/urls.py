from localsite import views

import django.contrib.auth.views
from django.conf.urls import url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^settings/', include('livesettings.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/', django.contrib.auth.views.login, {'template_name': 'admin/login.html'}),
    url(r'^$', views.index)
]
