import os
import sys
from pathlib import Path
import django
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

INNER_PIV_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INNER_PIV_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'piv.settings')

django.setup()

from messenger.consumers import ChatConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/messenger/<int:user_id>/', ChatConsumer.as_asgi()),
        ])
    ),
})