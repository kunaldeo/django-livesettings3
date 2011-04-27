Usage
=====

A very simple example project is in the directory :file:`livesettings/test_app`. It is almost identical to the following description and is a useful example for integrating livesettings into your app.

Creating Config.py
------------------

In order to use livesettings, you will need to create a :file:`config.py` in your django application. For this example, we will create a :file:`config.py` file in the 'myapp' directory.

For this specific app, we want to allow an admin user to control how many images are displayed on the front page of our site. We will create the following :file:`config.py`::

    from livesettings import config_register, ConfigurationGroup, PositiveIntegerValue, MultipleStringValue
    from django.utils.translation import ugettext_lazy as _

    # First, setup a grup to hold all our possible configs
    MYAPP_GROUP = ConfigurationGroup('MyApp', _('My App Settings'), ordering=0)

    # Now, add our number of images to display value
    # If a user doesn't enter a value, default to 5
    config_register(PositiveIntegerValue(
        MYAPP_GROUP,
            'NUM_IMAGES',
            description = _('Number of images to display'),
            help_text = _("How many images to display on front page."),
            default = 5
        ))

    # Another example of allowing the user to select from several values
    config_register(MultipleStringValue(
            MYAPP_GROUP,
            'MEASUREMENT_SYSTEM',
            description=_("Measurement System"),
            help_text=_("Default measurement system to use."),
            choices=[('metric',_('Metric')),
                        ('imperial',_('Imperial'))],
            default="imperial"
        ))

In order to activate this file, add the following line to your :file:`models.py`::

    import config
    
You can now see the results of your work by running the dev server and going to `settings <http://127.0.0.1:8000/settings/>`_ ::

    python manage.py runserver
    
Accessing your value in a view
------------------------------

Now that you have been able to set a value and allow a user to change it, the next step is to access it from a view. 

In a :file:`views.py`, you can use the config_value function to get access to the value. Here is a very simple view that passes the value to your template::


    from django.shortcuts import render_to_response
    from livesettings import config_value

    def index(request):
        image_count = config_value('MyApp','NUM_IMAGES')
        # Note, the measurement_system will return a list of selected values
        # in this case, we use the first one
        measurement_system = config_value('MyApp','MEASUREMENT_SYSTEM')
        return render_to_response('myapp/index.html', 
                                {'image_count': image_count,
                                'measurement_system': measurement_system[0]})

Using the value in your :file:`index.html` is straightforward::

    <p>Test page</p>
    <p>You want to show {{image_count}} pictures and use the {{measurement_system}} system.</p>


Restricting Access to Livesettings
----------------------------------

In order to give non-superusers access to the settings, make sure to use the django user permission admin screen to give the desired user the *livesettings|setting|Can change settting*.

.. Note::
    Superusers will have access to this setting without enabling any specific permissions

Permissions for insert, delete or permission for longsetting are ignored and only the above-mentioned permission is used.

Exporting Settings
------------------

Settings can be exported by the `http://127.0.0.1:8000/settings/export/ <http://127.0.0.1:8000/settings/export/>`_ . After exporting the file, the entire
output can be manually copied and pasted to :file:`settings.py` in order to deploy configuration to more sites or to entirely prevent further changes.
If you restrict DB access to the settings, all of the livesettings_* tables will be unused. 

Here is a simple example of what the extract will look like::

    LIVESETTINGS_OPTIONS = \
    {   1: {   'DB': False,
               'SETTINGS': {   u'MyApp': {   u'DECIMAL_TEST': u'34.0923443',
                                             u'MEASUREMENT_SYSTEM': u'["metric"]',
                                             u'PERCENT_TEST': u'0.251'}}}}

In order to restrict or enable DB access, use the following line in your settings::

    'DB': True,    # or False

If you have multiple sites, they can be manually combined in the file as well.

Next Steps
----------

The rest of the various livesettings types can be used in a similar manner. You can review the `satchmo code <https://bitbucket.org/chris1610/satchmo/src>`_ for more advanced examples.

.. _`Django-Keyedcache`: http://bitbucket.org/bkroeze/django-keyedcache/
.. _`Satchmo Project`: http://www.satchmoproject.com
.. _`pip`: http://pypi.python.org/pypi/pip
