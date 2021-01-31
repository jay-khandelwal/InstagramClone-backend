from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chatSystem.routing

from chatSystem.token_auth import TokenAuthMiddlewareStack, TokenAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chatSystem.routing.websocket_urlpatterns
        )
    ),
})

