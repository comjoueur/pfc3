
import json
from channels.generic.websocket import WebsocketConsumer
from pfc2.core.models import Client, Touch, Button
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pfc2 import utils


class ActionConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None

    def connect(self):
        self.client = Client.objects.create(channel_ws=self.channel_name,
                                            token=Client.generate_valid_client_token())
        self.accept()

    def disconnect(self, close_code):
        self.client.delete()

    def receive(self, text_data=None, bytes_data=None):
        if text_data == 'token':
            credentials = {
                'token': self.client.token,
            }
            self.send(text_data=json.dumps(credentials))

    def send_message(self, message):
        self.send(text_data=message['message'])


class ControllerConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.desktop_client = None

    def connect(self):
        self.client = Client.objects.create(channel_ws=self.channel_name,
                                            token=Client.generate_valid_client_token())
        self.accept()
        for kind in Button.DEFAULT_POSITION.keys():
            button = Button.objects.create(kind=kind, client=self.client)
            button.center = Button.DEFAULT_POSITION[kind]
            button.save()

    def disconnect(self, code):
        self.client.delete()

    def receive(self, text_data=None, bytes_data=None):
        data = text_data.split(':')
        if data[0] == 'token':
            self.desktop_client = Client.objects.filter(token=data[1]).first()

        if not self.desktop_client:
            return

        if data[0] == 'action':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(self.desktop_client.channel_ws, {
                'type': 'send.message',
                'message': json.dumps({'key': utils.keyCode[data[1]]})
            })

        elif data[0] == 'touch':
            button = Button.objects.filter(client=self.client, kind=data[3]).first()
            touch = Touch.objects.create(
                button=button,
                position_x=int(data[1].split('.')[0]) if '.' in data[1] else int(data[1]),
                position_y=int(data[2].split('.')[0]) if '.' in data[2] else int(data[2]),
                client=self.client
            )
            if button is None:
                touch.set_relative_button()
                touch.save()
            if self.client.touches.count() % 30 == 0 and Client.ADAPTATION_MODE:
                self.client.update_buttons()
                button_positions = self.client.get_buttons_positions()
                if button_positions:
                    self.send(text_data=json.dumps(button_positions))
