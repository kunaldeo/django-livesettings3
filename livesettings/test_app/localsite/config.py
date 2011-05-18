from livesettings import config_register, ConfigurationGroup, IntegerValue, PositiveIntegerValue, MultipleStringValue, ModuleValue
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

config_register(ModuleValue(
        MYAPP_GROUP,
        'MODULE',
        #description=_("Measurement System"),
        #help_text=_("Default measurement system to use."),
        default="django"
    ))

config_register(IntegerValue(
    MYAPP_GROUP,
        'SOME_INTEGER',
        description = _('Some integer value'),
        help_text = _("It can be also negative."),
    ))
