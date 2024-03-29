try:
    from django.shortcuts import render_to_response as render
except ImportError:
    from django.shortcuts import render

from livesettings.functions import config_value


def index(request):
    image_count = config_value('MyApp', 'NUM_IMAGES')
    # Note, the measurement_system will return a list of selected values
    # in this case, we use the first one
    measurement_system = config_value('MyApp', 'MEASUREMENT_SYSTEM')
    image_url = config_value('Images', 'IMAGE_URL')
    example_url = config_value('Urls', 'EXAMPLE_URL')
    return render('myapp/index.html',
                  {'image_count': image_count,
                   'measurement_system': measurement_system[0],
                   'image_url': image_url,
                   'example_url': example_url
                   })

