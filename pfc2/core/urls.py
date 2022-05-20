
from django.urls import path, include
from pfc2.core import views
from pfc2.core import consumers


urlpatterns = [
    path('', views.pacman_view),
    path('api/controller/<str:token>/', views.ControllerAPIView.as_view(), name="controller_api"),
    path('controller/', views.controller_view)
]

websocket_urlpatterns = [
    path('socket_action/', consumers.ActionConsumer.as_asgi()),
    path('controller_action/', consumers.ControllerConsumer.as_asgi())
]
