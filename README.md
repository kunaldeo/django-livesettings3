django-livesettings3
=====
[![Build Status](https://travis-ci.org/kunaldeo/django-livesettings3.svg?branch=master)](https://travis-ci.org/kunaldeo/django-livesettings3) [![PyPI version](https://badge.fury.io/py/django-livesettings3.svg)](https://badge.fury.io/py/django-livesettings3) [![codecov.io](https://codecov.io/github/kunaldeo/django-livesettings3/coverage.svg?branch=master)](https://codecov.io/github/kunaldeo/django-livesettings3?branch=master)

This is a Python 3 Port of django-livesettings that has been tested with Python 3.X and Django up to 4.X.

**django-livesettings3** provides the ability to configure settings via an admin interface, rather than by editing settings.py. In addition, livesettings allows you to set sane defaults so that your site can be perfectly functional without any changes. Livesettings uses caching to make sure this has minimal impact on your site’s performance. Finally, if you wish to lock down your site and disable the settings, you can export your livesettings and store them in your settings.py. This allows you have flexibility in deciding how various users interact with your app.

## Requirements
- Python 3.6+
- Django 1.8+
- [django-keyedcache3](https://github.com/kunaldeo/django-keyedcache3)

## Install
```
$ pip install git+https://github.com/kunaldeo/django-livesettings3
```
## Quickstart

### Adding livesettings to your project

Add livesettings to `settings.py`

```python
INSTALLED_APPS = (
  'django.contrib.admin',
  'livesettings',
  'myapp'
)
```
> It is high recommended to configure a global cache (like Redis) in production for multiprocess servers or you will see the outdated data.

Add `livesettings.urls` to urlpatterns in `urls.py`

```python
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', include('livesettings.urls')),
]
```

> Checkout the [Sample screenshot of livesetting editor](https://github.com/kunaldeo/django-livesettings3/wiki/Sample-Settings-Editor-Screenshot)

### Create `config.py`
Create `config.py` within your app directory where your `models.py` is located. We will use `config.py` to register the settings value.

`config.py`

```python
from django.utils.translation import gettext_lazy as _
from livesettings.functions import config_register
from livesettings.values import ConfigurationGroup, PositiveIntegerValue, MultipleStringValue


# Config group to hold all the configs
MYAPP_GROUP = ConfigurationGroup('MyApp', _('My App Settings'), ordering=0)

# When ordering parameter is not passed, all inputs are sorted by name
config_register(PositiveIntegerValue(
    MYAPP_GROUP,
    'NUM_IMAGES',
    description=_('Number of images to display'),
    help_text=_("How many images to display on front page."),
    # if no help_text is given, Default falue is displayed
    default=5
))

# Another example of allowing the user to select from several values
config_register(MultipleStringValue(
    MYAPP_GROUP,
    'MEASUREMENT_SYSTEM',
    description=_("Measurement System"),
    help_text=_("Default measurement system to use."),
    choices=[('metric', _('Metric')),
             ('imperial', _('Imperial'))],
    default="imperial"
))

```

### Activate `config.py`
To activate the `config.py` you need to import `config` from `models.py` file.

```python
from * import config
```

> Linter Warning: Becareful of PyCharm's `Optimize Imports`, it may remove this line as it is never called directly!

### Accessing Values in view

You can use `config_value` method to read the values store in livesttings

```python
from django.shortcuts import render
from livesettings.functions import config_value


def index(request):
    image_count = config_value('MyApp', 'NUM_IMAGES')
    # Note, the measurement_system will return a list of selected values
    # in this case, we use the first one
    measurement_system = config_value('MyApp', 'MEASUREMENT_SYSTEM')
    return render(request, 'myapp/index.html',
                  {'image_count': image_count,
                   'measurement_system': measurement_system[0]})
```

## Security and Permissions

In order to give non-superusers access to the /settings/ views, open Django Admin Auth screen and give the user or to its group the permission livesettings|setting|Can change settting. 

> Checkout the [permissions screenshot](https://github.com/kunaldeo/django-livesettings3/wiki/django-livesettings3-Permissions)

The same permission is needed to view the form and submit. Permissions for insert or delete and any permissions for “long setting” are ignored.

> Superusers will have access to this setting without enabling any specific permissions.

If you want to save a sensitive information to livesettings on production site (e.g. a password for logging into other web service) it is recommended not to grant permissions to livesettings to users which are logging in everyday. The most secure method is to export the settings and disable web access to livesettings as described below. Exporting settings itself is allowed only by the superuser.

> Because of the security significance of livesettings, all views in livesettings support CSRF regardless of whether or not the CsrfViewMiddleware is enabled or disabled.

## Exporting Settings

Settings can be exported by the `http://127.0.0.1:8000/settings/export/` . After exporting the file, the entire output can be manually copied and pasted to `settings.py`.

## Supported Data Types

Following Data Types are supported:

- Boolean
- Decimal
- Duration
- Float
- Integer
- Positive Integer (non negative)
- String
- Long string
- Multiple strings
- Long multiple strings
- Module values
- Password

>List is not implemented. But it is easy to use with comma separated string. When using the value you can simply use `csvstring.split(',')`

Fork of [https://bitbucket.org/bkroeze/django-livesettings](https://bitbucket.org/bkroeze/django-livesettings).
