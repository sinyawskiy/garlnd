async def reset_devices(pool):
    '''
    This function disconnect all devices on tracker daemon reboot.
    '''
    print('Reset connection addresses of devices')
    async with pool.acquire() as connection:
        result = await connection.execute('UPDATE devices_device SET connection_address=NULL WHERE TRUE;')
        return result


async def select_device_key(pool, device_key):
    print('Select device by key {}'.format(device_key))
    async with pool.acquire() as connection:
        result = await connection.fetchrow('SELECT id FROM devices_device WHERE add_position_password=$1 AND connection_address IS NULL LIMIT 1;', f'{device_key}')
        return result


async def reset_connection_address(pool, device_id):
    print('Reset connection address device id {}'.format(device_id))
    async with pool.acquire() as connection:
        result = await connection.execute('UPDATE devices_device SET connection_address=NULL WHERE id=$1;', device_id)
        return result


async def set_connection_address(pool, device_id, connection_address):
    print('Set connection address {} device id {}'.format(connection_address, device_id))
    async with pool.acquire() as connection:
        result = await connection.execute('UPDATE devices_device SET connection_address=$1 WHERE id=$2;', connection_address, device_id)
        return result


async def load_rules(pool, device_id):
    print('Load rules device id {}'.format(device_id))
    async with pool.acquire() as connection:
        result = await connection.fetchrow('SELECT id, rule_type, auto_reactivate, max_speed, initial_latitude, initial_longitude, distance_offset FROM rules_rule WHERE device_id=$1 AND is_active IS TRUE;', device_id)
        return result


async def select_previous_position(pool, device_id, previous_position_date):
    print('Select prevoius position {}'.format(device_id))
    async with pool.acquire() as connection:
        result = await connection.fetchrow(
            '''
                SELECT id, longitude, latitude, speed, created_at
                FROM positions_position
                WHERE is_broken=FALSE AND device_id=$1 AND created_at>$2
                ORDER BY id DESC LIMIT 1;''',
            device_id, previous_position_date)
        return result


async def insert_position(pool, device):
    print('Insert position {}'.format(device.id))
    async with pool.acquire() as connection:
        result = await connection.fetchrow('''
            INSERT INTO positions_position (device_id, longitude, longitude_type, latitude, latitude_type, distance, speed, acceleration, duration, is_broken, created_at, parameters)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id;
            ;''',
                device.id,
                device._position.longitude,
                device._position.longitude_type,
                device._position.latitude,
                device._position.latitude_type,
                device._distance,
                device._speed,
                device._acceleration,
                device._duration,
                device._is_broken,
                device._position.position_date,
                device._position.parameters

        )
        return result


async def update_position(pool, device):
    print('Update position {}'.format(device.id))
    async with pool.acquire() as connection:
        result = await connection.execute('''
            UPDATE positions_position SET device_id=%s, longitude=%s, longitude_type=%s, latitude=%s, latitude_type=%s, distance=%s, speed=%s, acceleration=%s, duration=%s, is_broken=%s, created_at=%s, parameters=%s
            WHERE id = %s;''', (
                device.id,
                device._position.longitude,
                device._position.longitude_type,
                device._position.latitude,
                device._position.latitude_type,
                device._distance,
                device._speed,
                device._acceleration,
                device._duration,
                device._is_broken,
                device._position.position_date,
                device._position.parameters,
                device._position.id
            )
        )
        return result
