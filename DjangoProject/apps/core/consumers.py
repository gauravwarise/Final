
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync
# from .models import StockDetail
import copy
import json
import asyncio
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

# class StockConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.room_name = "test_consumer"
#         self.room_group_name = "testw_consumer_group"

#         async_to_sync(self.channel_layer.group_add)(
#             self.room_name, self.room_group_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         pass

#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             message = text_data_json['message']
#         except json.JSONDecodeError as e:
#             print(f"Error decoding JSON: {e}")
#             return

#         print(f"Recieved message {message}")

#         await self.send(text_data=json.dumps({
#             'message': f"Youb said: {message}"
#         }))





class StockConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = "test_consumer"
        self.room_group_name = "testw_consumer_group"

        user = self.scope["user"]

        user_role = await sync_to_async(lambda: self.scope["session"].get('role', None))()
        print("===================>", user, user_role)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        print(f"Recieved message {message}")

        # await self.send(text_data=json.dumps({
        #     'message': f"Youb said: {message}"
        # }))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast.message',
                'message': message
            }
        )

    async def broadcast_message(self, event):
        # Send the message to the WebSocket
        print("inside brodcaster")
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': f"You said: {message}"
        }))


    # def connect(self):
    #     # Make a database row with our channel name
    #     # Clients.objects.create(channel_name=self.channel_name)
    #     pass

    # def disconnect(self, close_code):
    #     # Note that in some rare cases (power loss, etc) disconnect may fail
    #     # to run; this naive example would leave zombie channel names around.
    #     # Clients.objects.filter(channel_name=self.channel_name).delete()


    # def chat_message(self, event):
    #     # Handles the "chat.message" event when it's sent to us.
    #     # self.send(text_data=event["text"])