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

Settings are accessible by the URL http://your.site/settings/
Required permissions are 'livesettings | setting | Can change setting' or to be superuser,
similar like permissions for for other models in /admin/ are set.
Permissions for insert, delete or permission for longsetting are ignored and only the above-mentioned permission is applied for all.

Settings can be exported by the URL http://your.site/settings/export/ .
The whole output can be manually copied and pasted to 'settings.py' and the tables
livesettings_* would be accessed for that site never more. 
The switching between fixed values and values stored in the database is done by the line
    'DB': True,    # or False
Results for more sites can be for an eventually multi-site configuration manually combined.

.. _`Satchmo Project`: http://www.satchmoproject.com
