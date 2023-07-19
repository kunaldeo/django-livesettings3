from django.contrib.auth import views as auth_views
from django.contrib import admin
try:
    from django.urls import re_path, include
except ImportError:
    from django.conf.urls import url as re_path, include

urlpatterns = [
    re_path(r'^settings/', include('livesettings.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='loginview'),
]
