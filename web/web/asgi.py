# uvicorn pogoda_feed.asgi:application --ws websockets --http httptools
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker pogoda_feed.asgi:application

from .wsgi import *
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import hazard_feed.routing
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            hazard_feed.routing.websocket_urlpatterns
        )
    ),
})