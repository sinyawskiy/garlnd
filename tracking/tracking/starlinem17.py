import datetime
import asyncio
import asyncpg
from base import Device, GarlndProtocol
from device_queries import reset_devices
from settings import DATABASES
from starline.protocol import parse_ide, parse_work

DATABASE = DATABASES['default']

AUTH_PACKET = 0x41
WORK_PACKET = 0x02

server_task_container = []


class StarlineProtocol(GarlndProtocol):
    CONNECTION_TIMEOUT = 30


class Starline(StarlineProtocol):
    def __init__(self, *args, **kwargs):
        print('Starline')
        super().__init__(*args, **kwargs)

    def device_authorized_complete(self):
        print('authorize complete')
        print('resp_crc={}'.format(chr(self._dec[18])))
        self.transport.write(bytes('resp_crc={}'.format(chr(self._dec[18])), 'utf8'))

    # async def protocol_authorize(self, loop, crc_dec):
    #     task = loop.create_task(self.device.authorize(self._connection_address))
    #     await task
    #     self.device_authorized_complete(crc_dec)

    def data_received(self, data):
        self.stop_connection_timeout()
        loop = asyncio.get_running_loop()
        print('Received {} from {}'.format(data, self._connection_address))
        dec = [item for item in bytearray(data)]
        print(dec)
        self._dec = dec
        if dec[0] == AUTH_PACKET:
            result = parse_ide(dec[1:18])
            print(result)
            self.system_type = result['dev_type']
            self.version_hw = result['hw_ver']
            self.version_sw = result['sw_ver']
            if not self.device:
                self.device = Device(result['imei'], self.pool)
            if not self.device.is_authorized(self._connection_address):
                loop.create_task(self.device.authorize(self._connection_address))
            self.device_authorized_complete()
                # loop.create_task(self.protocol_authorize(loop, dec[18]))

        if dec[0] == WORK_PACKET:
            result = parse_work(dec[1:33])
            print(result)
            if result['gps_status'] == 'Real coordinates':
                loop.create_task(
                    self.device.update_position(
                        result['long']['coords'],
                        result['lat']['coords'],
                        datetime.datetime.fromtimestamp(int(result['date'])),
                        normalized_coordinates=True,
                        speed=result['velocity'],
                        battery=result['Bat'],
                        temperature=result['Temp'],
                        power=result['Power'],
                        system_type=self.system_type,
                        version_hw=self.version_hw,
                        version_sw=self.version_sw,
                    )
                )

        self.restart_connection_timeout()


async def listen_tcp(pool):
    global server_task_container
    print('Listen TCP')
    loop = asyncio.get_running_loop()
    coro = loop.create_server(lambda: Starline(pool), '0.0.0.0', 12300)
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

