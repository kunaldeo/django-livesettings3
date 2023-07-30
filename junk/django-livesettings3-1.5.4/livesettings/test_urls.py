from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^settings/', include('livesettings.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='loginview'),
]
