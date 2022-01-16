import datetime
import asyncio
from aiohttp import web
import asyncpg
from aiohttp.web_app import Application

from base import Device
from device_queries import reset_devices
from settings import DATABASES

DATABASE = DATABASES['default']


class TraccarApplication(Application):
    def __init__(self, pool, *args, **kwargs):
        print('Traccar')
        super().__init__(*args, **kwargs)
        self.pool = pool

    # def data_received(self, data):
    #     print(data)
    #     print(r)
    #     # self.device = Device(self.args['id'][0])
    #     # connection_address = getClientIP(self)
    #     # if self.device.is_authorized(connection_address):
    #     #     self.device_authorized_complete()
    #     # else:
    #     #     self.device.authorize(connection_address).addCallbacks(self.device_authorized_complete, self.device_not_authorized)
    #     #
    #     self.restart_connection_timeout()

    # def finish_request(self):
    #     self.setResponseCode(200)
    #     self.setHeader(b"content-type", b"text/html; charset=utf-8")
    #     print('Device finish request {}'.format(self.device.id))
    #     return self.finish()
    #
    # def device_not_authorized(self, *args):
    #     print('Device not authorized {}'.format(self.device.id))
    #     return self.finish_request()
    #
    # def device_authorized_complete(self, *args):
    #     print('Device authorized {}'.format(self.device.id))
    #     self.device.update_position(
    #         float(self.args['lon'][0]),
    #         float(self.args['lat'][0]),
    #         datetime.datetime.fromtimestamp(int(self.args['timestamp'][0])),
    #         speed=self.args['speed'][0],
    #         accuracy=self.args['accuracy'][0],
    #         batt=self.args['batt'][0],
    #         bearing=self.args['bearing'][0],
    #         altitude=self.args['altitude'][0]
    #     )
    #     return self.finish_request()

async def index_handler(request):
    params = request.rel_url.query
    device = Device(params['id'], request.app.pool)
    connection_address = request.remote
    print('Received {} from {}'.format(params, connection_address))
    if not device.is_authorized(connection_address):
        try:
            await device.authorize(connection_address)
        except Exception:
            print('Device not authorized {}'.format(params['id']))
            return web.Response(status=200)
    else:
        print('Device authorized {}'.format(device.id))
        await device.update_position(
            float(params['lon']),
            float(params['lat']),
            datetime.datetime.fromtimestamp(int(params['timestamp'])),
            speed=params['speed'],
            accuracy=params['accuracy'],
            batt=params['batt'],
            bearing=params['bearing'],
            altitude=params['altitude']
        )
        return web.Response(status=200)


async def listen_tcp(pool):
    global server_task_container
    print('Listen TCP')
    app = TraccarApplication(pool)
    app.router.add_post("/", index_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    srv = web.TCPSite(runner, host='0.0.0.0', port=6006)
    await srv.start()

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

