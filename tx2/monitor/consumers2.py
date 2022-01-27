import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CameraLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope)
        self.flight_name = self.scope['url_route']['kwargs']['camera_log']
        self.room_group_name = 'camera_log_%s' % self.flight_name
        print(self.room_group_name)
        print('channel name', self.channel_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def camera_log_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
