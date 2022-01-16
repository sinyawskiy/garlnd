import random
import string
# import urllib, urllib2, simplejson
from django.db import connection
# from django.utils.encoding import smart_str
# from django.conf import settings

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

#
# def get_lat_lng_google(location):
#
#     # http://code.google.com/p/gmaps-samples/source/browse/trunk/geocoder/python/SimpleParser.py?r=2476
#
#     location = urllib.quote_plus(smart_str(location))
#     url = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=%s' % location
#     response = urllib2.urlopen(url).read()
#     result = simplejson.loads(response)
#     if result['status'] == 'OK':
#         lat = str(result['results'][0]['geometry']['location']['lat'])
#         lng = str(result['results'][0]['geometry']['location']['lng'])
#         return [lng, lat]
#     else:
#         return None
#
#
# def get_lat_lng_yandex(location):
#
#     # http://api.yandex.ru/maps/doc/geocoder/desc/concepts/input_params.xml
#
#     location = urllib.quote_plus(smart_str(location))
#     url = 'http://geocode-maps.yandex.ru/1.x/?format=json&key=%s&results=1&geocode=%s' % (settings.YANDEX_MAPS_API_KEY, location)
#     response = urllib2.urlopen(url).read()
#     result = simplejson.loads(response)
#     if len(result['response']['GeoObjectCollection']['featureMember']):
#         return str(result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']).split(' ')
#     else:
#         return None


def get_pos(location):
    map_obj_query = '''
        SELECT count(*), `addresses`.`longitude`, `addresses`.`latitude`
        FROM `addresses_address` `addresses` WHERE `addresses`.`geocoder_address` = '%s' LIMIT 1;
    ''' % location
    cursor = connection.cursor().cursor
    cursor.execute(map_obj_query)
    map_obj_arr = cursor.fetchone()
    if map_obj_arr[0]:
        pos = [map_obj_arr[2], map_obj_arr[1]]
    else:
        pos = get_lat_lng_yandex(location)
        if pos is None:
            pos = get_lat_lng_google(location)
    return pos


def paddTo(input_str, pad_len, filler='0'):
    str_len = len(input_str)
    if str_len < pad_len:
        input_str = '%s%s' % (filler*(pad_len-str_len), input_str)
    return input_str