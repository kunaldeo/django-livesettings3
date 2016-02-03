[![Build Status](https://travis-ci.org/kunaldeo/django-livesettings3.svg?branch=master)](https://travis-ci.org/kunaldeo/django-livesettings3)
About
=====

Python 3 Port of django-livesettings that has been tested with Python 3.5.1 and Django 1.9.2. 

It provides the ability to configure settings via an admin interface, rather than by editing settings.py. In addition, livesettings allows you to set sane defaults so that your site can be perfectly functional without any changes. Livesettings uses caching to make sure this has minimal impact on your site’s performance.

Finally, if you wish to lock down your site and disable the settings, you can export your livesettings and store them in your settings.py. This allows you have flexibility in deciding how various users interact with your app.

Livesettings supports several types of input choices:

> -   Boolean
> -   Decimal
> -   Duration
> -   Float
> -   Integer
> -   Positive Integer (non negative)
> -   String
> -   Long string
> -   Multiple strings
> -   Long multiple strings
> -   Module values
> -   Password

Livesettings has been used for many years in the satchmo project and is considered stable and production ready.

Fork of [https://bitbucket.org/bkroeze/django-livesettings](https://bitbucket.org/bkroeze/django-livesettings).
