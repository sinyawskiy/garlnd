import datetime
import asyncio
import asyncpg
from findme.protocol import convert_work
from base import Device, GarlndProtocol
from device_queries import reset_devices
from settings import DATABASES

DATABASE = DATABASES['default']

AUTH_PACKET = 0x10
WORK_PACKET = 0x11
BLACK_BOX_PACKET = 0x12

server_task_container = []


class Findme(GarlndProtocol):
    def __init__(self, *args, **kwargs):
        print('Autofon')
        super().__init__(*args, **kwargs)

    def device_authorized_complete(self):
        print('authorize complete')
        self.transport.write(bytes('resp_crc={}'.format(str(self._dec[11])), 'utf8'))

    def data_received(self, data):
        self.stop_connection_timeout()
        loop = asyncio.get_running_loop()
        print('Received {} from {}'.format(data, self._connection_address))
        dec = [item for item in bytearray(data)]
        self._dec = dec
        if dec[0] == AUTH_PACKET:
            imei = ''.join(str(hex(x)[2:].zfill(2)) for x in dec[3:11]).strip('0')
            self.system_type = str(int(bin(dec[1])[2:].zfill(8)[:4], 2))
            self.version_hw = str(int(bin(dec[1])[2:].zfill(8)[4:], 2))
            self.version_sw = chr(int(dec[2]))
            if not self.device:
                self.device = Device(imei, self.pool)
            if not self.device.is_authorized(self._connection_address):
                loop.create_task(self.device.authorize(self._connection_address))
            self.device_authorized_complete()

        if dec[0] == WORK_PACKET:
            result = convert_work(dec)
            print(result)
            if result[0]['gpsValid'] == 'yes':
                loop.create_task(
                    self.device.update_position(
                        result[0]['gpsLong'],
                        result[0]['gpsLat'],
                        datetime.datetime.fromtimestamp(int(result[0]['gpsTime'])),
                        normalized_coordinates=True,
                        speed=result[0]['gpsSpeedKm'],
                        altitude=result[0]['gpsAltMeter'],
                        battery=result[0]['battery'],
                        temperature=result[0]['oCtemp'],
                        power=result[0]['power'],
                        motion=result[0]['motion'],
                        system_type=self.system_type,
                        version_hw=self.version_hw,
                        version_sw=self.version_sw,
                    )
                )

        if dec[0] == BLACK_BOX_PACKET:
            pass
        self.restart_connection_timeout()



async def listen_tcp(pool):
    global server_task_container
    print('Listen TCP')
    loop = asyncio.get_running_loop()
    coro = loop.create_server(lambda: Findme(pool), '0.0.0.0', 5005)
    server_task = loop.create_task(coro)
    server_task_container.append(server_task)

    # print('serving on %s' % (coro.sockets[0].getsockname(),))

# def signalHandler(signum, stackframe):
#     global trackers_listeners
#     log.msg('Stop listening')
#     if trackers_listeners:
#         for trackers_listener in trackers_listeners:
#             trackers_listener.stopListening()
#
#     resetDevices(callback=stopReactorAfterResetDevices)


# def stopReactorAfterResetDevices(*args):
#     reactor.callFromThread(reactor.stop)


async def init_app():
    pool = await asyncpg.create_pool(
        host=DATABASE['HOST'],
        port=DATABASE['PORT'],
        database=DATABASE['NAME'],
        user=DATABASE['USER'],
        password=DATABASE['PASSWORD'],
    )
    await reset_devices(pool)
    await listen_tcp(pool)


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signalHandler)
    # resetDevices(callback=startListenTCPAfterResetDevices)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    print('inited')
    loop.run_forever()

