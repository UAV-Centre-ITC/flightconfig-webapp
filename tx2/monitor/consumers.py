import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CameraLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #print(self.scope)
        #self.room_name = self.scope['url_route']['kwargs']['flight_name']
        #print(self.room_name)
        #self.room_group_name = '{}_camera_log'.format(self.room_name)
        #print(self.room_group_name)
        self.channel_group_name = 'camera-log'
    
        # Join the group
        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.channel_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['data']

        # Send message to room group
        await self.channel_layer.group_send(
            self.channel_group_name,
            {
                'type': 'camera_log_message',
                'data': message
            }
        )

    # Receive message from room group
    async def camera_log_message(self, event):
        message = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': message
        }))

