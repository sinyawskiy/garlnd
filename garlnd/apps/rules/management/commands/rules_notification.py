# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
import math
from django.db import connection
from devices.models import Device
from django.conf import settings
from positions.models import Position

degrees_to_radians = math.pi/180.0

def distance_between_positions_method1(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    else:
        # phi = 90 - latitude
        phi1 = (90.0 - lat1)*degrees_to_radians
        phi2 = (90.0 - lat2)*degrees_to_radians

        # theta = longitude
        theta1 = lon1*degrees_to_radians
        theta2 = lon2*degrees_to_radians

        # Compute spherical distance from spherical coordinates.

        # For two locations in spherical coordinates
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) =
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length

        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
               math.cos(phi1)*math.cos(phi2))
        arc = math.acos(cos)
        return arc*6371


def distance_between_positions_method3(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    else:

        phi1 = lat1*degrees_to_radians
        phi2 = lat2*degrees_to_radians
        delta_lon = lon2*degrees_to_radians - lon1*degrees_to_radians
        delta_lat = phi2 - phi1
        a = (math.sin(delta_lat/2))**2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lon/2))**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return c*6371

def distance_between_positions_method2(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    else:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lon = math.radians(lon2) - math.radians(lon1)
        delta_lat = phi2 - phi1
        a = (math.sin(delta_lat/2))**2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lon/2))**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return c*6371

class Command(BaseCommand):
    help = 'Set distance, speed, acceleration, grumms_factor'
    args = '<port>'

    def handle(self, *args, **options):
        for device in Device.objects.all():

            for position in Position.objects.filter(device=device):
                previous_position_date = position.created_at - datetime.timedelta(seconds=settings.TIME_DELTA_BETWEEN_TRACKS)

                cursor = connection.cursor()
                cursor.execute('SELECT `longitude`, `latitude`, `distance`, `speed`, `acceleration`, `created_at`, `id` FROM `positions_position` WHERE `is_broken`=0 AND `device_id`=%s AND `created_at`>=%s AND `created_at`<=%s AND `id`!=%s ORDER BY `created_at` DESC LIMIT 1;',
                    (device.id, previous_position_date.strftime('%Y-%m-%d %H:%M:%S'), position.created_at.strftime('%Y-%m-%d %H:%M:%S'), position.id)
                )
                previous_coordinates = cursor.fetchone()
                cursor.close()

                distance = 0
                speed = 0
                acceleration = 0
                duration = 0
                is_broken = False
                previous_id = 0

                if previous_coordinates:
                    previous_id = previous_coordinates[6]
                    time_diff = position.created_at - previous_coordinates[5]
                    duration = time_diff.seconds
                    if duration != 0:
                        distance = distance_between_positions_method2(previous_coordinates[1], previous_coordinates[0], position.latitude, position.longitude)
                        speed = (distance*3600)/duration
                        acceleration = (speed - previous_coordinates[3])/(duration*3.6)
                        is_broken = 1 if abs(acceleration) > settings.MAX_ABS_ACCELERATION else 0

                cursor = connection.cursor()
                cursor.execute('UPDATE `positions_position` SET `is_broken`=%s, `distance`=%s, `speed`=%s, `acceleration`=%s, `duration`=%s WHERE `id`=%s;', (is_broken, speed, distance, acceleration, duration, position.id))
                cursor.close()

                print('id:%d prev id:%d time: %d dist: %f sp %f acc %f' % (position.id, previous_id, duration, distance, speed, acceleration))


