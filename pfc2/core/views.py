
import json
from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from pfc2 import utils
from pfc2.core.models import Client
from pfc2.core.serializers import ClientSerializer


def pacman_view(request):
    if request.method == 'GET':
        return render(request, 'pacman.html')


def controller_view(request):
    if request.method == 'GET':
        return render(request, 'controller.html')


class ControllerAPIView(RetrieveAPIView):
    serializer_class = ClientSerializer

    def get_object(self):
        token = self.kwargs['token']
        client = Client.objects.filter(token=token).first()
        action = self.request.query_params.get('action')
        action = utils.keyCode.get(action, None)
        if action and client.pk:
            action = {
                'key': action,
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(client.channel_ws, {
                'type': 'send_message',
                'message': json.dumps(action)
            })
        return client
