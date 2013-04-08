Installation
============

Requirements
------------

 * `Python`_ 2.5+, 2.6+ or 2.7+
 * `Django`_ 1.4+ or 1.5+
 * `Django-Keyedcache`_

.. Note 
    It is recommended you use `pip`_ for the install process.


Installing Livesettings
-----------------------

After the dependencies have been installed, you can install the latest livesettings, using::

    pip install -e hg+http://bitbucket.org/bkroeze/django-livesettings/#egg=django-livesettings

Add livesettings to your installed apps in :file:`settings.py`::

    INSTALLED_APPS = (
        ...
        # Uncomment the next line to enable the admin:
        'django.contrib.admin',
        'livesettings',
        'myapp'
        ...
    )

It is high recommended to configure a global cache (like `MemcachedCache`) for
multiprocess servers! Otherwise the processes would not be notified about new
values with the default `LocMemCache`. The default configuration is safe for
a debug server (manage.py runserver).


Add it to your :file:`urls.py`::

    urlpatterns = patterns('',
        ...
        # Uncomment the next line to enable the admin:
        url(r'^admin/', include(admin.site.urls)),
        url(r'^settings/', include('livesettings.urls')),
        ...
    )
    
Execute a syncdb to create the required tables::

    python manage.py syncdb
    

.. _`Django-Keyedcache`: http://bitbucket.org/bkroeze/django-keyedcache/
.. _`pip`: http://pypi.python.org/pypi/pip
.. _`Python`: http://www.python.org/
.. _`Django`: http://www.djangoproject.com/
