import json
from urllib.parse import quote
from django import forms
from django.utils import safestring

class ImageInput(forms.FileInput):

    def __init__(self, *args, **kwargs):
        """ImageInput.__init__ function takes
        an optional parameter url_resolver
        which must be a callable accepting one argument - the url
        or url key
        url_resolver must return a valid image url

        if not given or None, the resolver will be a dummy
        fuction returning an unchanged value
        """
        self.url_resolver = kwargs.pop('url_resolver')
        super(ImageInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        output = '<div style="margin: 0 auto; max-width: 100%; position: relative;">'
        output += '<img style="object-fit: cover; width: 100%; max-height: 350px;"'
        if attrs and 'image_class' in attrs:
            output += ' class="%s"' % attrs['image_class']
        output += ' src="%s"/><br/>' % self.url_resolver(value)
        output += super(ImageInput, self).render(name, value, attrs)
        output += '</div>'
        return safestring.mark_safe(output)


class StringArrayWidget(forms.TextInput):
    """StringArrayWidget is a widget for editing a list of strings"""
    template_name = 'livesettings/form_widgets/string_array_widget.html'

    def __init__(self, *args, default=None, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        """Returns context for rendering"""
        context = super().get_context(name, value, attrs)
        context['value'] = value.strip('"')
        context['widget']['default'] = quote(json.dumps(self.default))
        return context
