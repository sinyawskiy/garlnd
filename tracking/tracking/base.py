import asyncio
import copy
import json
import math
from datetime import datetime, timedelta

from device_queries import reset_connection_address, set_connection_address, load_rules, \
    select_previous_position, insert_position, update_position, select_device_key
from settings import TORNADING_PORT, TORNADING_KEY, MAX_ABS_ACCELERATION, TIME_DELTA_BETWEEN_TRACKS, GARLND_HOST
from aiohttp import ClientSession, ClientConnectorError
from rule_queries import deactivate_rule, notification_without_position, notification_with_position

TIMEOUT = 60*3  # 15*60
BUSY_TIMEOUT = 1


class GarlndProtocol(asyncio.Protocol):
    CONNECTION_TIMEOUT = 10

    def __init__(self, pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = pool
        self._dec = []
        self.connection_timeout = None
        self.device = None

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        self._connection_address = '{}:{}'.format(peername[0], peername[1])
        print('Connection from {}'.format(self._connection_address))
        self.restart_connection_timeout()

    def restart_connection_timeout(self):
        loop = asyncio.get_running_loop()
        if self.connection_timeout:
            self.connection_timeout.cancel()
        self.connection_timeout = loop.call_later(self.CONNECTION_TIMEOUT, lambda: self.disconnect('timeout'))

    def stop_connection_timeout(self):
        if self.connection_timeout:
            self.connection_timeout.cancel()
            self.connection_timeout = None

    def connection_lost(self, exc):
        if exc:
            print('connection lost', exc)
        else:
            print('connection lost')

    def disconnect(self, message):
        print(message)
        self.stop_connection_timeout()
        self.transport.close()


class RulesTypesEnum(object):
    """ copied from rules models RulesTypesEnum
    """
    GEO_ZONE_OUT = 1  # Выход из Гео-зоны
    GEO_ZONE_IN = 2  # Вход в Гео-зону
    DRIVE_START = 3  # Начало движения
    MAX_SPEED = 4  # Максимальная скорость
    DISCONNECT = 5  # Отключние трэкера
    CONNECT = 6  # Включение трэкера


async def fetch(url, title):
    print('{} - {}'.format(title, url))
    async with ClientSession() as session:
        try:
            async with session.get(url) as response:
                print('{} - {}'.format(title, url))
                return await response.read()
        except ClientConnectorError:
            print('Not connection to host')


class Position(object):
    def __init__(self, latitude, longitude, position_date=None, **kwargs):
        self._id = None
        if kwargs.get('normalized_coordinates'):
            self._latitude = float(latitude)
            self._longitude = float(longitude)
        else:
            self._latitude = float(self.normalize_coordinate(latitude))
            self._longitude = float(self.normalize_coordinate(longitude))
        self._position_date = position_date if position_date is not None else datetime.utcnow()
        self._other_parameters = json.dumps(kwargs)
        print('New position %s %s' % (self.get_coordinates(), self._position_date.strftime('%Y-%m-%d %H:%M:%S')))
        print('Other parameters: {}'.format(self._other_parameters))

    @property
    def latitude(self):
        return self._latitude

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def longitude(self):
        return self._longitude

    @property
    def position_date(self):
        return self._position_date

    @property
    def parameters(self):
        return self._other_parameters or ''

    @property
    def longitude_type(self):
        return 'E' if self._longitude >= 0 else 'W'

    @property
    def latitude_type(self):
        return 'N' if self._latitude >= 0 else 'S'

    def get_coordinates(self):
        return [self.latitude, self.longitude]

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.latitude == other.latitude and self.longitude == other.longitude and self.position_date == other.position_date
        else:
            return False

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def get_distance(position1, position2):
        if position1 == position2:
            return 0
        else:
            phi1 = math.radians(position1.latitude)
            phi2 = math.radians(position2.latitude)
            delta_lon = math.radians(position2.longitude) - math.radians(position1.longitude)
            delta_lat = phi2 - phi1
            a = (math.sin(delta_lat / 2)) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lon / 2)) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return c * 6371

    @staticmethod
    def normalize_coordinate(coordinate):
        if coordinate < -180.0:
            return 180.0 + coordinate % 180.0
        elif coordinate > 180.0:
            return 180.0 - coordinate % 180.0
        return coordinate % 180.0


class Rule(object):
    def __init__(self, pool, rule_id, rule_type, auto_reactivate, max_speed=None, initial_latitude=None,
                 initial_longitude=None, distance_offset=None):
        self.pool = pool
        self._is_active = True
        self._id = rule_id
        self._rule_type = rule_type
        self._auto_reactivate = auto_reactivate
        if rule_type == RulesTypesEnum.GEO_ZONE_OUT or rule_type == RulesTypesEnum.GEO_ZONE_IN:
            self._geo_zone_position = Position(initial_latitude, initial_longitude)
            self._distance_offset = distance_offset  # радиус зоны км
            self._is_device_in_geo_zone = False if rule_type == RulesTypesEnum.GEO_ZONE_OUT else True
        elif rule_type == RulesTypesEnum.MAX_SPEED:
            self._max_speed = max_speed
        print('Load rule type %s rule id: %s' % (self._rule_type, self._id))

    def rule_deactivated(self, affected_rows):
        print('Deactivate rule id: %s, deactivated %s' % (self._id, affected_rows))

    async def deactivate(self):
        self._is_active = False
        result = await deactivate_rule(self.pool, self._id)
        self.rule_deactivated(result)

    def apply(self, position, previous_position, speed, previous_speed, is_connected):
        fired = False
        if self._is_active:
            if self._rule_type == RulesTypesEnum.GEO_ZONE_OUT and position is not None:
                is_device_in_geo_zone = Position.get_distance(self._geo_zone_position, position) < self._distance_offset
                if self._is_device_in_geo_zone and not is_device_in_geo_zone:
                    print('Geo zone out fired rule id: %s' % self._id)
                    self.create_notification(position.id)
                    fired = True
                self._is_device_in_geo_zone = is_device_in_geo_zone

            elif self._rule_type == RulesTypesEnum.GEO_ZONE_IN and position is not None:
                is_device_in_geo_zone = Position.get_distance(self._geo_zone_position, position) < self._distance_offset
                if not self._is_device_in_geo_zone and is_device_in_geo_zone:
                    print('Geo zone in fired rule id: %s' % self._id)
                    self.create_notification(position.id)
                    fired = True
                self._is_device_in_geo_zone = is_device_in_geo_zone

            elif self._rule_type == RulesTypesEnum.DRIVE_START and position is not None:
                if previous_speed < 20 < speed:
                    print('Drive start fired rule id: %s' % self._id)
                    self.create_notification(position.id)
                    fired = True

            elif self._rule_type == RulesTypesEnum.MAX_SPEED and position is not None:
                if speed > self._max_speed:
                    print('Max speed fired rule id: %s' % self._id)
                    self.create_notification(position.id)
                    fired = True

            elif self._rule_type == RulesTypesEnum.DISCONNECT:
                if not is_connected:
                    print('Disconnect fired rule id: %s' % self._id)
                    self.create_notification()
                    fired = True

            elif self._rule_type == RulesTypesEnum.CONNECT:  # fired one time
                if is_connected:
                    print('Connect fired rule id: %s' % self._id)
                    self.create_notification()
                    self._is_active = False
                    fired = True

        if fired and not self._auto_reactivate:
            self.deactivate()

    def notification_created(self, query_result):
        print('Created notification id: %s' % query_result)

    async def create_notification(self, position_id=None):
        if position_id is not None:
            result = await notification_with_position(self.pool, self._id, position_id)
            self.notification_created(result)
        else:
            result = await notification_without_position(self.pool, self._id)
            self.notification_created(result)


class Device(object):
    devices = {}
    _device_key = None
    DELETE_TIMEOUT = 60*3

    def __new__(cls, *args):
        device_password = args[0]
        if device_password not in cls.devices:
            print('create new')
            cls.devices[device_password] = object.__new__(cls)
        return cls.devices[device_password]

    @classmethod
    def delete_device_from_class(cls, device_key):
        print(f'delete device from class {device_key}')
        try:
            device = cls.devices[device_key]
            del cls.devices[device_key]
            del device
        except KeyError:
            pass

    def __init__(self, device_password, pool):
        self.pool = pool
        if not self._device_key:
            self._device_id = None  # For rules and map
            self._device_key = device_password  # For key devices
            self._is_authorized = False
            self._delete_timeout = None
            self._is_busy = False

            # positions
            self._previous_position = None
            self._position = None

            # additional parameters
            self._duration = 0
            self._distance = 0
            self._speed = 0
            self._previous_speed = 0
            self._acceleration = 0
            self._is_broken = False
            self._rules = []
            self._connection_address = None
            self.delete_timeout = None
            self.restart_delete_timeout()  # not authorized device
            print('__init__ new device key {}'.format(device_password))
        else:
            print('__init__ get device key {}'.format(device_password))
            print(self)

    @property
    def id(self):
        return self._device_id

    async def timeout_task(self, delay, func):
        await asyncio.sleep(delay)
        await func()

    def restart_delete_timeout(self):
        print('restart delete device timeout')
        loop = asyncio.get_running_loop()
        if self.delete_timeout:
            self.delete_timeout.cancel()
        self.delete_timeout = loop.create_task(self.timeout_task(self.DELETE_TIMEOUT, self._timeout_delete_device))

    def stop_delete_timeout(self):
        if self.delete_timeout:
            self.delete_timeout.cancel()
            self.delete_timeout = None

    def is_authorized(self, connection_address):
        if self._is_authorized:
            if self._connection_address != connection_address:
                loop = asyncio.get_running_loop()
                loop.create_task(self._update_connection_address(connection_address))
        return self._is_authorized

    async def authorize(self, connection_address):  # external deferred method
        if not self._is_busy:
            self._is_busy = True
            await self._check_device_id_and_set_connection_address(self._device_key, connection_address)
        else:
            await asyncio.sleep(BUSY_TIMEOUT)
            await self.authorize(connection_address)

    async def update_position(self, longitude, latitude, timestamp, **kwargs):  # external deferred method
        if not self._is_busy:
            self._is_busy = True
            await self._update_current_position(latitude, longitude, timestamp, **kwargs)
        else:
            await asyncio.sleep(BUSY_TIMEOUT)
            await self.update_position(longitude, latitude, timestamp, **kwargs)

    async def _check_device_id_and_set_connection_address(self, device_key, connection_address):
        print('_check_device_id_and_set_connection_address - connection_address {}'.format(connection_address))
        query_result = await select_device_key(self.pool, device_key)
        await self._check_device_id(query_result, connection_address)

    async def _check_device_id(self, query_result, connection_address):
        if query_result and query_result['id'] and connection_address:
            self._device_id = query_result['id']
            print('_check_device_id - connection_address {} device_id {}'.format(connection_address, self._device_id))
            await self._update_connection_address(connection_address)
        else:
            raise Exception('Already connected or can not find this password or connection address is none')

    async def _update_connection_address(self, connection_address=None):
        print('_update_connection_address - connection_address {}'.format(connection_address))
        if connection_address is None:
            row_count = await reset_connection_address(self.pool, self._device_id)
            self._unset_connection_address_device_and_delete(row_count)
        else:
            row_count = await set_connection_address(self.pool, self._device_id, connection_address)
            await self._set_device_id_authorized_and_load_rules(row_count, connection_address)

    async def _timeout_delete_device(self):
        print('_timeout_disconnect - device id {}'.format(self._device_id))
        if self._device_id:
            await self._update_connection_address()
        else:
            self._delete_from_devices()

    def _set_state_is_authorized(self):
        print('_set_state_is_authorized - device id {}'.format(self._device_id))
        self._is_authorized = True
        self._apply_rules()
        self._update_device_status_on_map()
        self._is_busy = False
        self.restart_delete_timeout()

    def _unset_connection_address_device_and_delete(self, row_count):
        print('_unset_connection_address_device_and_delete - device id {}, affected rows {}'.format(self._device_id, row_count))
        self._delete_device('unset address')

    def _delete_device(self, reason):
        print('_delete_device - reason: %s' % reason)
        self._connection_address = None
        self._apply_rules()
        self._update_device_status_on_map()
        self._delete_from_devices()

    def _delete_from_devices(self):
        print('_delete_from_devices - device_key {}'.format(self._device_key))
        self.stop_delete_timeout()
        self.__class__.delete_device_from_class(self._device_key)

    def _load_rules(self, query_result):
        self._rules = []
        if query_result:
            for row in query_result:
                self._rules.append(
                    Rule(row['id'], row['rule_type'], row['auto_reactivate'], row['max_speed'], row['initial_latitude'], row['initial_longitude'], row['distance_offset']))
        print('_load_rules - count of rules {}'.format(len(self._rules)))
        return self._set_state_is_authorized()

    async def _set_device_id_authorized_and_load_rules(self, row_count, connection_address):
        print('_set_device_id_authorized_and_load_rules - connection_address {} affected rows {}'.format(connection_address, row_count))
        self._connection_address = connection_address
        query_result = await load_rules(self.pool, self._device_id)
        return self._load_rules(query_result)

    def _apply_rules(self):
        print('_apply_rules - device id {}'.format(self._device_id))
        for rule in self._rules:
            rule.apply(self._position, self._previous_position, self._speed, self._previous_speed, self._connection_address is not None)

    def _update_parameters(self):
        #aware - naive
        time_diff = self._position.position_date - self._previous_position.position_date.replace(tzinfo=None)
        if time_diff.seconds < TIME_DELTA_BETWEEN_TRACKS:
            self._duration = time_diff.seconds

            if self._duration != 0:
                self._distance = Position.get_distance(self._position, self._previous_position)
                self._previous_speed = self._speed if self._speed else 0
                self._speed = (self._distance*3600)/self._duration
                self._acceleration = (self._speed - self._previous_speed)/(self._duration*3.6)
                self._is_broken = True if abs(self._acceleration) > MAX_ABS_ACCELERATION else False

    async def _update_parameters_and_save_position(self):
        if self._previous_position is not None:
            self._update_parameters()
        await self._save_position()

    async def _set_previous_position(self, query_row):
        if query_row:  # may be none
            row = dict(zip(['id', 'longitude', 'latitude', 'speed', 'created_at'], query_row))
            self._previous_position = Position(row['latitude'], row['longitude'], row['created_at'])
            self._previous_position.id = row['id']
            self._previous_speed = row['speed']
            await self._update_parameters_and_save_position()
        else:
            await self._save_position()

    async def _load_previous_position_and_previous_speed_from_db(self):
        previous_position_date = self._position.position_date-timedelta(seconds=TIME_DELTA_BETWEEN_TRACKS)
        result = await select_previous_position(self.pool, self._device_id, previous_position_date)
        await self._set_previous_position(result)

    async def _update_current_position(self, latitude, longitude, position_date, **kwargs):
        if self._position is not None and not self._is_broken:
            self._previous_position = copy.deepcopy(self._position)

        self._position = Position(latitude, longitude, position_date, **kwargs)
        if self._position != self._previous_position:
            if self._previous_position is None:
                await self._load_previous_position_and_previous_speed_from_db()
            else:
                await self._update_parameters_and_save_position()
        else:
            print('Position not changed')
            self._is_busy = False
        self.restart_delete_timeout()

    def _update_position_id(self, position_id):
        print('Position id set: %s' % position_id)
        self._position.id = position_id
        self._update_position_on_map()
        self._is_busy = False

    def _position_updated(self, affected_rows):
        print('Position updated, affected rows %s' % affected_rows)
        if self._previous_position is not None:
            self._apply_rules()
        self._update_position_on_map()
        self._is_busy = False

    async def _save_position(self):
        if not self._position.id:
            result = await insert_position(self.pool, self)
            self._update_position_id(result['id'])
        else:
            result = await update_position(self.pool, self)
            self._position_updated(result)

    def _update_position_on_map(self):
        url = 'http://%(garlnd_host)s:%(port)d/positions/update_on_map/%(position_id)s/%(tornading_key)s/' % {
            'garlnd_host': GARLND_HOST,
            'port': TORNADING_PORT,
            'position_id': self._position.id,
            'tornading_key': TORNADING_KEY
        }
        fetch_task = fetch(url, 'update_position_on_map')
        loop = asyncio.get_running_loop()
        loop.create_task(fetch_task)

    def _update_device_status_on_map(self):
        url = 'http://%(garlnd_host)s:%(port)d/devices/update_on_map/%(device_id)s/%(status_id)s/%(tornading_key)s/' % {
            'garlnd_host': GARLND_HOST,
            'port': TORNADING_PORT,
            'device_id': self._device_id,
            'status_id': 0 if self._connection_address is None else 1,
            'tornading_key': TORNADING_KEY
        }
        fetch_task = fetch(url, 'update_device_status_on_map')
        loop = asyncio.get_running_loop()
        loop.create_task(fetch_task)
