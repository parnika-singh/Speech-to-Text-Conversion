"""
ASGI config for asr_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

#entry point for websocket connections
 
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import realtime_comparator.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asr_project.settings')

#application = get_asgi_application()
application=ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            realtime_comparator.routing.websocket_urlpatterns
        )
    ),
})