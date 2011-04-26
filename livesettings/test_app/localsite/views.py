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
