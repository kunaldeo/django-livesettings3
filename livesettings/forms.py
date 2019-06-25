import logging

from django import forms

log = logging.getLogger('configuration')


class SettingsEditor(forms.Form):
    "Base editor, from which customized forms are created"

    def __init__(self, *args, **kwargs):
        from livesettings.values import ConfigurationGroup

        settings = kwargs.pop('settings')
        super(SettingsEditor, self).__init__(*args, **kwargs)
        flattened = []
        groups = []
        for setting in settings:
            if isinstance(setting, ConfigurationGroup):
                for s in setting:
                    flattened.append(s)
            else:
                flattened.append(setting)

        for setting in flattened:
            # Add the field to the customized field list
            kw = {
                'label': setting.description,
                'help_text': setting.help_text,
                # Provide current setting values for initializing the form
                'initial': setting.editor_value
            }
            field = setting.make_field(**kw)

            k = '%s__%s' % (setting.group.key, setting.key)
            self.fields[k] = field
            if not setting.group in groups:
                groups.append(setting.group)
                # log.debug("Added field: %s = %s" % (k, str(field)))

        self.groups = groups


class LocalizedChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        #self.language_code = kwargs.pop('language_code',
        #                                django_settings.LANGUAGE_CODE)
        super(LocalizedChoiceField, self).__init__(*args, **kwargs)


class LocalizedMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        #self.language_code = kwargs.pop('language_code',
        #                                django_settings.LANGUAGE_CODE)
        super(LocalizedMultipleChoiceField, self).__init__(*args, **kwargs)
