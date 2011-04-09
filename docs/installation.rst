Installation
============

Requirements
------------

 * `Python`_ 2.5 or higher
 * `Django`_ 1.2.3 or higher
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
