from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class GameRoom(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = 'room_%s' % self.room_name
        print(self.room_group_name)

        async_to_sync(self.channel_layer.group_add)(
            #self.room_name,
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({'status' :'connected from django channels'}))

    def disconnect(self,*args,**kwargs):
        print('disconnected')

    def receive(self, text_data):
        print(text_data)
        self.send(text_data=json.dumps(text_data))


    def run_game(self, event):
        data = event['payload']
        data = json.loads(data)

        self.send(text_data=json.dumps({
            'payload': data['data']
        }))

