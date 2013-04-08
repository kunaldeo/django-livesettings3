"""Examples for livesettings"""

from livesettings.values import *
from livesettings import config_register, config_register_list
from django.utils.translation import ugettext_lazy as _

# Default values should be specified explicitely, otherwise it would be
# an error if nothing is saved in the database and no default is found.

# First, setup a group to hold all our possible configs
MYAPP_GROUP = ConfigurationGroup('MyApp', _('My App Settings'), ordering=0)

# Now, add our number of images to display value
# If a user doesn't enter a value, default to 5
config_register(PositiveIntegerValue(
    MYAPP_GROUP,
        'NUM_IMAGES',
        description = _('Number of images to display'),
        help_text = _("How many images to display on front page."),
        # if no help_text is given, Default falue is displayed
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

# Because we did not used "ordering" for values, all inputs are sorted alphabetically by name



# Example group for different boxes

from decimal import Decimal

_ = lambda x: x  # example of dummy international translation function


GR1_BOX = ConfigurationGroup('gr_box', _('Example of different boxes'), ordering=1)

config_register_list(

    # Texbox - string or many other types
    StringValue( GR1_BOX, 'my_StringValue', description='Textbox', ordering=1, default='Orange',
        help_text='StringValue and many different types looks similar'),

    # Textarea - LongStringValue can be longer then 255 characters
    LongStringValue( GR1_BOX, 'my_LongStringValue', description='Textarea', ordering=2, default='something',
        help_text='Long String value'),

    # Checkbox - Boolean
    BooleanValue( GR1_BOX, 'my_BooleanValue', description='Check box',  ordering=3, default=True,
        help_text='Boolean value'),

    # Combobox - String value with choices
    StringValue( GR1_BOX, 'my_StringValue_combobox', description='Combobox', ordering=4,
         help_text='String value with choices',
         default=u'AUTO',
         choices=(('ELEPHANT', _('Elephant')), ('ANT', _('Ant')), ('AUTO', _('Autodetect')),)),

    # Listbox with multiple selection - MultipleStringValue with choices
    MultipleStringValue( GR1_BOX, 'my_MultipleStringValue', 
        description='Listbox - e.g. Required Fields', ordering=5, help_text='MultipleStringValue with choices',
        default=['email', 'first_name'],
        choices=(
            ('email', _("Email")),
            ('title', _("Title")),
            ('first_name', _("First name")),
            ('last_name', _("Last name")),
        )),

    # Password displayed like '****'.
    PasswordValue( GR1_BOX, 'my_PasswordValue', description='Password value', ordering=6,
        default='only to see *** now', render_value=True),
    # If render_value=True (default) the widget will be pre-filled with an actual password value displayed like "****".
    # If render_value=False, the password field is not pre-filled with any value
    # and an actual value can be removed by writing space to the field (which is converted to empty string).

)


# Examples of other types

GR_MORE = ConfigurationGroup('gr_more', _('More examples'), ordering=2)

config_register_list(

    IntegerValue( GR_MORE, 'my_IntegerValue', description='Integer value', ordering=1, default=-12),
    # Input values are converted to int type.

    PositiveIntegerValue( GR_MORE, 'my_PositiveIntegerValue', description='Positive integer value',
        ordering=2, default=13),
    # PositiveIntegerValue(...) is the same as IntegerValue(..., mini_value=0) 

    DecimalValue( GR_MORE, 'my_DecimalValue', description='Decimal value', ordering=3,
        default=Decimal('1.2300')),
    # Input values are converted to type decimal.Decimal
    # Possible default values are e.g. '4', '4.0', Decimal('4.0'), 4, etc.

    DurationValue( GR_MORE, 'my_DurationValue', description='Duration value',
        help_text='datetime type, input in second', ordering=4, default=25 * 3600.0),
    # Input value in seconds is converted to type datetime.timedelta

    FloatValue( GR_MORE, 'my_FloatValue', description='Float value', ordering=5,
        default=3.14),
    # Input values are converted to type float.

    LongMultipleStringValue( GR_MORE, 'my_LongMultipleStringValue',
        description='Long Multiple String Value with choices',  ordering=6,
        default=['blablabla_b', 'blablabla_c'],
        choices= tuple(('blablabla_' + x, 15 * x) for x in 'abcdefghijklmnopqrstuvwxyz'),
        # This example requires storage in long string if all options are selected.
        ),
    # Combined Long and Multiple StringValue
)


# Example of conditional items (fiels or modules) that can by enabled/disabled
# by selecting in some choises list.
# These contitional items and their corresponding choice for enable/disable can
# be independently installed/uninstalled by adding a new config.py file (like
# plugins - without modifying another file)
# (Here is the second part under the line below.)

GR_MY_CONDITIONAL = ConfigurationGroup('MY_CONDITIONAL', 
        _('Enable and configure conditional modules'), ordering=3)

# Every module can have its own set of specific live settings, which are enabled/disabled together with a module.

MY_CONDITIONAL_SWITCHES = MultipleStringValue(GR_MY_CONDITIONAL, 'MODULES',
        description=_('Conditional modules'),
        choices=(('calendar', 'Calendar module'),),
        default=['calendar',],
        help_text='Enable/Disable some of these modules and press Update to see more/less settings fields or groups',
    )

# A contitionally displayed field
config_register_list(
    MY_CONDITIONAL_SWITCHES,

    StringValue(GR_MY_CONDITIONAL, 'first_day', description='Calendar - First day of week', default='Monday',
        ordering=1,
        choices=zip(* 2 * (('Sunday', 'Monday'),)),
        requires=MY_CONDITIONAL_SWITCHES,
        requiresvalue='calendar',
        help_text = 'Visibility of this field depends on selecting the item "Calendar" above.'
    )

)

# ==========================================================================================
# This part is usually located in a separate file control.py in optional's module directory
# and can be completely removed. That only removes some one conditional group and its
# choice in MY_CONDITIONAL_SWITCHES.

from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import *

# add a new choice to main choises where this module can be enabled
MY_CONDITIONAL_SWITCHES = config_get('MY_CONDITIONAL', 'MODULES')
MY_CONDITIONAL_SWITCHES.add_choice(('django.contrib.webdesign.lorem_ipsum', 'Random text module'))

# create a conditional configuration group and some item.
MY_FIRST_OPTIONAL_GROUP = ConfigurationGroup('django.contrib.webdesign.lorem_ipsum',
    _('Random Text Module Settings'),
    requires = MY_CONDITIONAL_SWITCHES,
    requiresvalue='django.contrib.webdesign.lorem_ipsum',
    ordering = 101)

config_register_list(
    ModuleValue(MY_FIRST_OPTIONAL_GROUP, 'MODULE', default='django.contrib.webdesign.lorem_ipsum', hidden=True),

    MultipleStringValue(MY_FIRST_OPTIONAL_GROUP, 'lorem_words', description='Random words',
        choices= zip(* 2 * ('lorem ipsum dolor sit amet'.split(),)),
        help_text = 'Visibility of this group depends on selecting the item "Random text module" above.',
    )
)

# More examples for modules in "https://bitbucket.org/chris1610/satchmo/src/tip/satchmo/apps/payment/modules/"
