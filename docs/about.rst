About
=====

Django-Livesettings is a project split from the `Satchmo Project`_.  It provides the ability to configure settings via an admin interface, rather than by editing :file:`settings.py`. In addition, livesettings allows you to set sane defaults so that your site can be perfectly functional without any changes. Livesettings uses caching to make sure this has minimal impact on your site's performance.

Livesettings supports several types of input choices:

    * Boolean
    * Decimal
    * Duration
    * Float
    * Integer
    * Percent
    * Positive Integer
    * String
    * Long string
    * Multiple strings
    * Long multiple strings
    * Module values

Livesettings has been used for many years in the satchmo project and is considered stable and production ready.

Settings are accessible by the URL http://your.domain/settings/
Required permissions are 'livesettings | setting | Can change setting' or to be superuser,
similar like permissions for for other models in /admin/ are set.
Permissions for insert, delete or permission for longsetting are ignored and only the above-mentioned permission is applied for all.

.. _`Satchmo Project`: http://www.satchmoproject.com
