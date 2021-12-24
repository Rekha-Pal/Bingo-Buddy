"""
ASGI config for bingo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.conf.urls import url
from django.urls import path
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from student.consumers import GameRoom

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo.settings')

application = get_asgi_application()

ws_pattern = [
    path('student/test/<room_code>',GameRoom.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        'websocket':AuthMiddlewareStack(URLRouter(
            ws_pattern
        ))
    }
)
