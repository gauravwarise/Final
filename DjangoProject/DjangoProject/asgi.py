"""
ASGI config for DjangoProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
# from apps.core.routing import websocket_urlpatterns
from apps.core import routing 

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        SessionMiddlewareStack(
            URLRouter(
            # your routing here
            routing.websocket_urlpatterns
        )
        )
    ),
})


# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket":  AuthMiddlewareStack(
#                             SessionMiddlewareStack(
#                                URLRouter(
#             websocket_urlpatterns
#         )
#                                )                      
#                     ),
# })


