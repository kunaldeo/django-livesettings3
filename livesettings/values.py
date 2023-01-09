"""Taken and modified from the dbsettings project.

http://code.google.com/p/django-values/
"""
from decimal import Decimal
import os

from livesettings.forms import LocalizedMultipleChoiceField, LocalizedChoiceField
from livesettings.widgets import ImageInput

try:
    from collections import OrderedDict as SortedDict
except ImportError:
    from django.utils.datastructures import SortedDict

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from django import forms
from django.conf import settings as djangosettings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import storage
from django.db import connection, DatabaseError
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.translation import get_language as _get_language
from livesettings.models import find_setting, LongSetting, Setting, SettingNotSet
from livesettings.overrides import get_overrides
from livesettings.utils import load_module, is_string_like, is_list_or_tuple
import datetime
import logging
from . import signals

__all__ = ['BASE_GROUP', 'ConfigurationGroup', 'Value', 'BooleanValue', 'DecimalValue', 'DurationValue',
           'FloatValue', 'IntegerValue', 'ModuleValue', 'PercentValue', 'PositiveIntegerValue', 'SortedDotDict',
           'StringValue', 'LongStringValue', 'MultipleStringValue', 'LongMultipleStringValue', 'PasswordValue',
           'URLValue', 'ImageValue']

_WARN = {}
try:
    is_setting_initializing
except:
    is_setting_initializing = True  # until the first success find "livesettings_setting" table, by any thread

log = logging.getLogger('configuration')

# The constant NOTSET is a placeholder for an uninitialized value (which has no
# default in the user's application and no value in the database).
# It is different from None or "" which are result of an empty field in the form.
# It leads to to the existing more complicated code of Values classes, hopefully more robust.
NOTSET = object()


def get_language():
    return _get_language() or djangosettings.LANGUAGE_CODE


def format_setting_name(token):
    """Returns string in style in upper case
    with underscores to separate words"""
    token = token.replace(' ', '_')
    token = token.replace('-', '_')
    bits = token.split('_')
    return '_'.join(bits).upper()


class SortedDotDict(object):
    def __init__(self, *args, **kwargs):
        super(SortedDotDict, self).__init__(*args, **kwargs)
        self._dict = SortedDict()

    def __contains__(self, *args, **kwargs):
        return self._dict.__contains__(*args, **kwargs)

    def __eq__(self, *args, **kwargs):
        return self._dict.__eq__(*args, **kwargs)

    def __format__(self, *args, **kwargs):
        return self._dict.__format__(*args, **kwargs)

    def __ge__(self, *args, **kwargs):
        return self._dict.__ge__(*args, **kwargs)

    def __getattr__(self, key):
        try:
            return self._dict[key]
        except:
            raise AttributeError(key)

    def __iter__(self):
        vals = list(self.values())
        for k in vals:
            yield k

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def keys(self):
        return list(self._dict.keys())

    def values(self):
        vals = list(self._dict.values())
        vals = [v for v in vals if isinstance(v, (ConfigurationGroup, Value))]
        vals.sort()
        return vals

    def items(self):
        return list(self._dict.items())

    def iterkeys(self):
        return iter(self._dict.keys())

    def itervalues(self):
        return iter(self._dict.values())

    def iteritems(self):
        return iter(self._dict.items())

    def get(self, *args, **kwargs):
        return self._dict.get(*args, **kwargs)

    def clear(self):
        return self._dict.clear()

    def copy(self):
        s = SortedDotDict()
        s._dict = self._dict.copy()
        return s

    def fromkeys(self):
        return self._dict.fromkeys()

    def has_key(self, key):
        return key in self._dict

    def pop(self, *args, **kwargs):
        return self._dict.pop(*args, **kwargs)

    def popitem(self, *args, **kwargs):
        return self._dict.popitem(*args, **kwargs)

    def setdefault(self, key, default):
        return self._dict.setdefault(key, default)

    def update(self, d):
        return self._dict.update(d)

    def viewitems(self, *args, **kwargs):
        return self._dict.viewitems(*args, **kwargs)

    def viewvalues(self, *args, **kwargs):
        return self._dict.viewvalues(*args, **kwargs)


class SuperGroup(object):
    """Aggregates ConfigurationGroup's into super-groups
    that are used only for the presentation in the UI"""
    def __init__(self, name, ordering = 0):
        self.name = name
        self.ordering = ordering
        self.groups = list()

    def append(self, group):
        """adds instance of :class:`ConfigurationGroup`
        to the super group
        """
        if group not in self.groups:
            self.groups.append(group)


BASE_SUPER_GROUP = SuperGroup(_('Main'))

class ConfigurationGroup(SortedDotDict):
    """A simple wrapper for a group of configuration values"""

    def __init__(self, key, name, *args, **kwargs):
        """Create a new ConfigurationGroup.

        Arguments:
        - key
        - group name - for display to user

        Named Arguments:
        - ordering: integer, optional, defaults to 1.
        - requires: See `Value` requires.  The default `requires` all member values will have if not overridden.
        - requiresvalue: See `Values` requires_value.  The default `requires_value` if not overridden on the `Value` objects.
        """
        self.key = key
        self.name = name
        self.ordering = kwargs.pop('ordering', 1)
        self.requires = kwargs.pop('requires', None)
        self.super_group = kwargs.pop('super_group', BASE_SUPER_GROUP)
        self.super_group.append(self)
        if self.requires:
            reqval = kwargs.pop('requiresvalue', key)
            if not is_list_or_tuple(reqval):
                reqval = (reqval, reqval)

            self.requires_value = reqval[0]
            self.requires.add_choice(reqval)

        super(ConfigurationGroup, self).__init__(*args, **kwargs)

    def __lt__(self, other):
        return (self.ordering, self.name) < (other.ordering, other.name)

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.ordering == other.ordering
                and self.name == other.name)

    def __ne__(self, other):
        return not self == other

    def dict_values(self, load_modules=True):
        vals = {}
        keys = list(super(ConfigurationGroup, self).keys())
        for key in keys:
            v = self[key]
            if isinstance(v, Value):
                value = v.value
            else:
                value = v
            vals[key] = value
        return vals

    def values(self):
        vals = list(super(ConfigurationGroup, self).values())
        return [v for v in vals if v.enabled()]


BASE_GROUP = ConfigurationGroup('BASE', _('Base Settings'), ordering=0)


class Value(object):
    creation_counter = 0

    def __init__(self, group, key, **kwargs):
        """
        Create a new Value object for configuration.

        Args:
            - `ConfigurationGroup`
            - key - a string key

        Named arguments:
            - `description` - Will be passed to the field for form usage.  Should be a translation proxy.  Ex: _('example')
            - `help_text` - Will be passed to the field for form usage.
            - `choices` - If given, then the form field will use a select box
            - `ordering` - Defaults to alphabetical by key if not given.
            - `requires` - If given as a `Value`, then this field will only be rendered if that Value evaluates true (for Boolean requires) or the proper key is in the associated value.
            - `requiresvalue` - If set, then this field will only be rendered if that value is in the list returned by self.value. Defaults to self.key.
            - `hidden` - If true, then render a hidden field.
            - `default` - If given, then this Value will return that default whenever it has no associated `Setting`.
            - `update_callback` - if given, then this value will call the callback whenever updated
        """
        self.group = group
        self.key = key
        self.description = kwargs.get('description', None)
        self.help_text = kwargs.get('help_text')
        self.choices = kwargs.get('choices', [])
        self.ordering = kwargs.pop('ordering', 0)
        self.hidden = kwargs.pop('hidden', False)
        self.localized = kwargs.pop('localized', False)
        self.update_callback = kwargs.pop('update_callback', None)
        self.requires = kwargs.pop('requires', None)
        if self.requires:
            reqval = kwargs.pop('requiresvalue', key)
            if not is_list_or_tuple(reqval):
                reqval = (reqval, reqval)

            self.requires_value = reqval[0]
            self.requires.add_choice(reqval)

        elif group.requires:
            self.requires = group.requires
            self.requires_value = group.requires_value

        if 'default' in kwargs:
            self.default = kwargs.pop('default')
            self.use_default = True
        else:
            self.use_default = False

        self.creation_counter = Value.creation_counter
        Value.creation_counter += 1

    def __lt__(self, other):
        if self.description is None or other.description is None:
            return (self.ordering, self.creation_counter) < (self.ordering, self.creation_counter)
        return (self.ordering, self.description, self.creation_counter) < (
            other.ordering, other.description, other.creation_counter)

    def __eq__(self, other):
        if type(self) == type(other):
            return self.value == other.value
        else:
            return self.value == other

    def __iter__(self):
        return iter(self.value)

    def __unicode__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)

    def add_choice(self, choice):
        """Add a choice if it doesn't already exist."""
        if not is_list_or_tuple(choice):
            choice = (choice, choice)
        skip = False
        for k, v in self.choices:
            if k == choice[0]:
                skip = True
                break
        if not skip:
            self.choices += (choice,)

    def choice_field(self, **kwargs):
        if self.hidden:
            kwargs['widget'] = forms.MultipleHiddenInput()
        return LocalizedChoiceField(choices=self.choices, **kwargs)

    def _choice_values(self):
        choices = self.choices
        vals = self.value
        return [x for x in choices if x[0] in vals]

    choice_values = property(fget=_choice_values)

    def copy(self):
        new_value = self.__class__(self.group, self.key)
        new_value.__dict__ = self.__dict__.copy()
        return new_value

    def _default_text(self):
        if not self.use_default:
            note = ""
        else:
            if self.default == "":
                note = _('Default value: ""')

            elif self.choices:
                work = []
                for x in self.choices:
                    try:
                        if x[0] == self.default or x[0] in self.default:
                            work.append('%s' % str(smart_str(x[1])))
                    except TypeError:
                        continue
                note = gettext('Default value: ') + ", ".join(work)

            else:
                note = _("Default value: %s") % str(self.default)

        return note

    default_text = property(fget=_default_text)

    def enabled(self):
        enabled = False
        try:
            if not self.requires:
                enabled = True
            else:
                v = self.requires.value
                if self.requires.choices:
                    enabled = self.requires_value == v or self.requires_value in v
                elif v:
                    enabled = True
        except SettingNotSet:
            pass
        return enabled

    def make_field(self, **kwargs):
        if self.choices:
            if self.hidden:
                kwargs['widget'] = forms.MultipleHiddenInput()
            field = self.choice_field(**kwargs)
        else:
            if self.hidden:
                kwargs['widget'] = forms.HiddenInput()
            field = self.field(**kwargs)

        field.group = self.group
        field.default_text = self.default_text
        return field


    def make_setting_with_value(self, value, language_code=None):
        db_value = self.get_db_prep_save(value)
        return self.make_setting(db_value, language_code=language_code)

    def make_setting(self, db_value, language_code=None):
        log.debug('new setting %s.%s', self.group.key, self.key)
        key = self.key
        if self.localized:
            key += '_' + format_setting_name(language_code or get_language())
        return Setting(group=self.group.key, key=key, value=db_value)

    def _setting(self):
        key = self.key
        if self.localized:
            key += '_' + format_setting_name(get_language())
        return find_setting(self.group.key, key)

    setting = property(fget=_setting)

    def _value(self):
        global is_setting_initializing
        use_db, overrides = get_overrides()

        lang = get_language()

        key = self.key
        if self.localized:
            key += '_' + format_setting_name(lang)
        if not use_db:
            try:
                val = overrides[self.group.key][key]
            except KeyError:
                if self.use_default:
                    val = self.default
                else:
                    raise SettingNotSet('%s.%s is not in your LIVESETTINGS_OPTIONS' % (self.group.key, key))

        else:
            try:
                val = self.setting.value

            except SettingNotSet as sns:
                is_setting_initializing = False
                if self.use_default:
                    val = self.default
                    if overrides:
                        # maybe override the default
                        grp = overrides.get(self.group.key, {})
                        if self.key in grp:
                            val = grp[self.key]
                else:
                    val = NOTSET

            except AttributeError as ae:
                is_setting_initializing = False
                log.error("Attribute error: %s", ae)
                log.error("%s: Could not get _value of %s", self.key, self.setting)
                raise (ae)

            except Exception as e:
                global _WARN
                if is_setting_initializing and isinstance(e, DatabaseError) and str(e).find(
                        "livesettings_setting") > -1:
                    if 'livesettings_setting' not in _WARN:
                        log.warning(str(e).strip())
                        _WARN['livesettings_setting'] = True
                    log.warning('Error loading livesettings from table, OK if you are in syncdb or before it. ROLLBACK')
                    connection._rollback()

                    if self.use_default:
                        val = self.default
                    else:
                        raise ImproperlyConfigured("All settings used in startup must have defaults, %s.%s does not",
                                                   self.group.key, self.key)
                else:
                    is_setting_initializing = False
                    import traceback
                    traceback.print_exc()
                    log.error("Problem finding settings %s.%s, %s", self.group.key, self.key, e)
                    raise SettingNotSet("Startup error, couldn't load %s.%s" % (self.group.key, self.key))
            else:
                is_setting_initializing = False
        return val

    def update(self, value, language_code=None):
        use_db, overrides = get_overrides()

        if use_db:
            current_value = self.value

            new_value = self.to_python(value)
            if current_value != new_value:
                if self.update_callback:
                    new_value = self.update_callback(*(current_value, new_value))

                db_value = self.get_db_prep_save(new_value)

                try:
                    s = self.setting
                    s.value = db_value

                except SettingNotSet:
                    s = self.make_setting(db_value, language_code=language_code)

                if self.use_default and self.to_python(self.default) == self.to_python(new_value):
                    if s.id:
                        log.info("Deleted setting %s.%s", self.group.key, self.key)
                        s.delete()
                else:
                    log.info("Updated setting %s.%s = %s", self.group.key, self.key, value)
                    s.save()

                signals.configuration_value_changed.send(self.__class__, old_value=current_value, new_value=new_value,
                                                         setting=self)

                return True
        else:
            log.debug('not updating setting %s.%s - livesettings db is disabled', self.group.key, self.key)

        return False

    @property
    def value(self):
        val = self._value()
        return self.to_python(val)

    @property
    def editor_value(self):
        val = self._value()
        return self.to_editor(val)

    # Subclasses should override the following methods where applicable

    def to_python(self, value):
        "Returns a native Python object suitable for immediate use"
        if value == NOTSET:
            value = None
        return value

    def get_db_prep_save(self, value):
        "Returns a value suitable for storage into a CharField"
        if value == NOTSET:
            value = ""
        return str(value)

    def to_editor(self, value):
        "Returns a value suitable for display in a form widget"
        if value == NOTSET:
            return NOTSET  # TODO this was not a good idea for an editor: "<object object 0x123..>"
        return str(value)


###############
# VALUE TYPES #
###############

class BooleanValue(Value):
    class field(forms.BooleanField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.BooleanField.__init__(self, *args, **kwargs)

    def add_choice(self, choice):
        # ignore choice adding for boolean types
        pass

    def to_python(self, value):
        if value in (True, 't', 'True', 1, '1'):
            return True
        return False

    to_editor = to_python


class DecimalValue(Value):
    class field(forms.DecimalField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.DecimalField.__init__(self, *args, **kwargs)

        def clean(self, value):
            # Parent "clean" calls "DecimaField.to_python" which converts value to Decimal or None.
            value = super(DecimalValue.field, self).clean(value)
            if value == None:
                return Decimal("0")
            return Decimal(value)

    def to_python(self, value):
        if value == NOTSET:
            return Decimal("0")

        try:
            return Decimal(value)
        except TypeError as te:
            log.warning("Can't convert %s to Decimal for settings %s.%s", value, self.group.key, self.key)
            raise TypeError(te)

    def to_editor(self, value):
        if value == NOTSET:
            return "0"
        else:
            return str(value)


class DurationValue(Value):
    # DurationValue has a lot of duplication and ugliness because DurationField
    # probably never will be accepted into Django code (issue #2443).

    class field(forms.CharField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            forms.CharField.__init__(self, *args, **kwargs)

        def clean(self, value):
            if value == '':
                value = 0
            try:
                return datetime.timedelta(seconds=float(value))
            except (ValueError, TypeError):
                raise forms.ValidationError('This value must be a real number.')
            except OverflowError:
                raise forms.ValidationError('The maximum allowed value is %s' % datetime.timedelta.max)

    def to_python(self, value):
        if value == NOTSET:
            value = 0
        if isinstance(value, datetime.timedelta):
            return value
        try:
            return datetime.timedelta(seconds=float(value))
        except (ValueError, TypeError):
            raise forms.ValidationError('This value must be a real number.')
        except OverflowError:
            raise forms.ValidationError('The maximum allowed value is %s' % datetime.timedelta.max)

    def get_db_prep_save(self, value):
        if value == NOTSET:
            return NOTSET
        else:
            return str(value.days * 24 * 3600 + value.seconds + float(value.microseconds) / 1000000)


class FloatValue(Value):
    class field(forms.FloatField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.FloatField.__init__(self, *args, **kwargs)

    def to_python(self, value):
        if value in (NOTSET, None):
            value = 0
        return float(value)

    def to_editor(self, value):
        if value == NOTSET:
            return "0"
        else:
            return str(value)


class IntegerValue(Value):
    class field(forms.IntegerField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.IntegerField.__init__(self, *args, **kwargs)

    def to_python(self, value):
        if value in (NOTSET, None):
            value = 0
        return int(value)

    def to_editor(self, value):
        if value == NOTSET:
            return "0"
        else:
            return str(value)


# Deprecated PercentValue does not work good and can not be fixed
# without duplicating long modified parts of Django. #29
# It is better to Replace PercentValue(...) by DecimalValue(... min_value=0, max_value=100, max_decimal_places=2)
# and easily divide result value by 100 in the user application.
class PercentValue(Value):
    class field(forms.DecimalField):

        def __init__(self, *args, **kwargs):
            import warnings
            warnings.warn(
                "class livesettings.PercentValue is deprecated. It should be replaced in config.py by " \
                "DecimalValue(... min_value=0, max_value=100) and the result divided by 100 in the app.",
                DeprecationWarning
            )
            kwargs['required'] = False
            forms.DecimalField.__init__(self, 100, 0, 5, 2, *args, **kwargs)

        def clean(self, value):
            if value == '':
                value = 0
            value = super(forms.DecimalField, self).clean(value)
            try:
                value = Decimal(value)
            except:
                raise forms.ValidationError('This value must be a decimal number.')
            return str(Decimal(value) / 100)

        class widget(forms.TextInput):
            def render(self, name, value, attrs=None, renderer=None):
                # Place a percent sign after a smaller text field
                try:
                    value = str("%.2f" % (Decimal(value) * 100))
                except:
                    value = "N/A"
                attrs['size'] = attrs['max_length'] = 6
                return mark_safe(super(forms.TextInput, self).render(name, value, attrs) + '%')

    def to_python(self, value):
        if value == NOTSET:
            value = 0
        return Decimal(value)

    def to_editor(self, value):
        if value == NOTSET:
            return "0"
        else:
            return str(value)


class PositiveIntegerValue(IntegerValue):
    """Non negative integer value. (positive or zero)."""

    class field(forms.IntegerField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            kwargs['min_value'] = 0
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.IntegerField.__init__(self, *args, **kwargs)


class StringValue(Value):
    class field(forms.CharField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.CharField.__init__(self, *args, **kwargs)

    def to_python(self, value):
        if value == NOTSET:
            value = ""
        return str(value)

    to_editor = to_python


class PasswordValue(StringValue):
    """
    Configuration value of the type Password
    Usage:
        config_register(PasswordValue(group, key, description=None, help_text,... render_value=True))

        render_value    Determines whether the widget will have a value filled in when the form is re-displayed (default is True).
                        If render_value=False, a password can be also completely deleted by writing space to the field.
    """

    # class field is dynamically assigned to the instance as FieldRender or FieldNoRender
    class FieldRender(forms.CharField):
        render_value = True

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            kwargs['widget'] = forms.PasswordInput(render_value=self.render_value)
            forms.CharField.__init__(self, *args, **kwargs)

    class FieldNoRender(FieldRender):
        render_value = False

    def __init__(self, *args, **kwargs):
        # prevent modifiyng of update_callback
        save_update_callback = self.update_callback
        setattr(self, 'field',
                kwargs.pop('render_value', True) and PasswordValue.FieldRender or PasswordValue.FieldNoRender)
        super(PasswordValue, self).__init__(*args, **kwargs)
        self.update_callback = save_update_callback

    def update_callback(self, current_value, new_value):
        # An old password can be deleted only by one space.
        if not self.field.render_value:
            if new_value == '':
                return current_value
            elif new_value == ' ':
                return ''
        return new_value


class URLValue(Value):

    class field(forms.URLField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.URLField.__init__(self, **kwargs)



class LongStringValue(Value):
    class field(forms.CharField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            kwargs['widget'] = forms.Textarea()
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.CharField.__init__(self, *args, **kwargs)

    def make_setting(self, db_value, language_code=None):
        log.debug('new long setting %s.%s', self.group.key, self.key)
        key = self.key
        if self.localized:
            key += '_' + format_setting_name(language_code or get_language())
        return LongSetting(group=self.group.key, key=key, value=db_value)

    def to_python(self, value):
        if value == NOTSET:
            value = ""
        return str(value)

    to_editor = to_python


class ImageValue(StringValue):
    def __init__(self, *args, **kwargs):
        self.allowed_file_extensions = kwargs.pop(
            'allowed_file_extensions',
            ('jpg', 'gif', 'png')
        )
        self.upload_directory = kwargs.pop(
            'upload_directory',
            djangosettings.MEDIA_ROOT
        )
        self.upload_url = kwargs.pop(
            'upload_url',
            djangosettings.MEDIA_URL
        )
        self.url_resolver = kwargs.pop('url_resolver', lambda v: v)
        super(ImageValue, self).__init__(*args, **kwargs)

    class field(forms.FileField):
        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.allowed_file_extensions = kwargs.pop('allowed_file_extensions')
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            url_resolver = kwargs.pop('url_resolver')
            kwargs['widget'] = ImageInput(url_resolver = url_resolver)
            forms.FileField.__init__(self, *args, **kwargs)

        def clean(self, file_data, initial=None):
            if not file_data and initial:
                return initial
            (base_name, ext) = os.path.splitext(file_data.name)
            #first character in ext is .
            if ext[1:].lower() not in self.allowed_file_extensions:
                error_message = _('Allowed image file types are %(types)s') \
                        % {'types': ', '.join(self.allowed_file_extensions)}
                raise forms.ValidationError(error_message)

    def make_field(self, **kwargs):
        kwargs['url_resolver'] = self.url_resolver
        kwargs['allowed_file_extensions'] = self.allowed_file_extensions
        return super(ImageValue, self).make_field(**kwargs)

    def update(self, uploaded_file, language_code=None):
        """uploaded_file is an instance of
        django UploadedFile object
        """
        #0) initialize file storage
        file_storage_class = storage.get_storage_class()

        storage_settings = {}
        if djangosettings.DEFAULT_FILE_STORAGE == \
            'django.core.files.storage.FileSystemStorage':
            storage_settings = {
                'location': self.upload_directory,
                'base_url': self.upload_url
            }

        file_storage = file_storage_class(**storage_settings)

        #1) come up with a file name
        #todo: need better function here to calc name
        file_name = file_storage.get_available_name(uploaded_file.name)
        file_storage.save(file_name, uploaded_file)
        url = file_storage.url(file_name)

        old_file = self.value
        old_file = old_file.replace(self.upload_url, '', 1)
        old_file_path = os.path.join(self.upload_directory, old_file)
        if os.path.isfile(old_file_path):
            os.unlink(old_file_path)

        #saved file path is relative to the upload_directory
        #so that things could be easily relocated
        super(ImageValue, self).update(url, language_code=language_code)

class MultipleStringValue(Value):
    class field(forms.CharField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            self.language_code = kwargs.pop('language_code', djangosettings.LANGUAGE_CODE)
            forms.CharField.__init__(self, *args, **kwargs)

    def choice_field(self, **kwargs):
        kwargs['required'] = False
        return LocalizedMultipleChoiceField(choices=self.choices, **kwargs)

    def get_db_prep_save(self, value):
        if is_string_like(value):
            value = [value]
        return json.dumps(value)

    def to_python(self, value):
        if not value or value == NOTSET:
            return []
        if is_list_or_tuple(value):
            return value
        else:
            try:
                return json.loads(value)
            except:
                if is_string_like(value):
                    return [value]
                else:
                    log.warning('Could not decode returning empty list: %s', value)
                    return []

    to_editor = to_python


class LongMultipleStringValue(MultipleStringValue):
    def make_setting(self, db_value, language_code=None):
        log.debug('new long setting %s.%s', self.group.key, self.key)
        return LongSetting(group=self.group.key, key=self.key, value=db_value)


class ModuleValue(Value):
    """Handles setting modules, storing them as strings in the db."""

    class field(forms.CharField):

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            forms.CharField.__init__(self, *args, **kwargs)

    def load_module(self, module):
        """Load a child module"""
        value = self._value()
        if value == NOTSET:
            raise SettingNotSet(f"{self.group.key}.{self.key}")
        else:
            return load_module("%s.%s" % (value, module))

    def to_python(self, value):
        if value in (NOTSET, ''):
            v = {}  # TODO this was probably not a good idea
        else:
            try:
                v = load_module(value)
            except ImportError:
                v = ''
        return v

    def get_db_prep_save(self, value):
        return getattr(value, '__name__', '')

    def to_editor(self, value):
        if value == NOTSET:
            value = ""
        return value
