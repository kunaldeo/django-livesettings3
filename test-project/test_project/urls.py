from localsite import views

from django.contrib.auth import views as auth_views
try:
    from django.conf.urls import url as re_path, include
except ImportError:
    from django.urls import re_path, include

from django.conf import settings
from django.contrib import admin
from django.views import static

admin.autodiscover()

urlpatterns = [
    re_path(r'^settings/', include('livesettings.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(f'^{settings.MEDIA_URL.strip("/")}(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html')),
    re_path(r'^$', views.index)
]
