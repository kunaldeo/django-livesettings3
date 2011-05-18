# Django settings.
# If you have an existing project, then ensure that you modify local_settings-customize.py
# and import it from your main settings file. (from local_settings import *)
import os

DIRNAME = os.path.dirname(__file__)

DJANGO_PROJECT = 'test_app'
DJANGO_SETTINGS_MODULE = 'test_app.settings'

ADMINS = (
     ('', ''),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'ado_mssql'.
        'NAME': 'test.db',
    }
}

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#Image files will be stored off of this path
MEDIA_ROOT = os.path.join(DIRNAME, 'static/')
#MEDIA_ROOT = "/static"
# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = 'site_media'
MEDIA_URL="/static/"
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #"django.middleware.csrf.CsrfViewMiddleware",  # views in livesettings have enabled CSRF regardless of this setting
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.doc.XViewMiddleware",
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = ('django.contrib.auth.context_processors.auth',)

ROOT_URLCONF = 'test_app.urls'

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'livesettings',
    'keyedcache',
    'test_app.localsite',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DEBUG_TOOLBAR_CONFIG = {
   'INTERCEPT_REDIRECTS' : False,
}

CACHE_PREFIX = 'T'
CACHE_TIMEOUT = 300
# If you use logging with the level DEBUG in your application, prevent increasing
# of logging level of keyedcache by uncommenting the following:
#import logging
#logging.getLogger('keyedcache').setLevel(logging.INFO)
DEBUG = True
