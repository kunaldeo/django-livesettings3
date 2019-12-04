from localsite import views

from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views import static

admin.autodiscover()

urlpatterns = [
    url(r'^settings/', include('livesettings.urls')),
    url(r'^admin/', admin.site.urls),
    url(f'^{settings.MEDIA_URL.strip("/")}(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html')),
    url(r'^$', views.index)
]
