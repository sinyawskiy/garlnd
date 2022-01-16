import json
from urllib import parse
from channels.generic.websocket import AsyncWebsocketConsumer


class MapConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, message):
        user = self.scope["user"]
        query_string = parse.parse_qs(self.scope['query_string'].decode("utf-8"))
        group_name = f"map_{query_string['map_id'][0]}"
        print('connect', message, self.channel_name, group_name)
        await self.channel_layer.group_add(
            group_name,
            self.channel_name,
        )
        await super(MapConsumer, self).websocket_connect(message)

    async def update_map(self, event):
        message = event['message']
        print('send to client', message)
        # Send message to WebSocket
        await self.send(text_data=message)
