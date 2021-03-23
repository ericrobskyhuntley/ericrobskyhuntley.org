from opencage.geocoder import OpenCageGeocode
from django.conf import settings
from django.contrib.gis.geos import Point

def geocode_address(query):
    gc = OpenCageGeocode(settings.OPENCAGE_KEY)
    result = gc.geocode(query, no_annotations=1)
    if result and len(result):
        lng = result[0]['geometry']['lng']
        lat  = result[0]['geometry']['lat']
        return Point(lng, lat, srid=4326)
    else:
        return None