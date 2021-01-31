from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async

from urllib.parse import parse_qs

'''
@database_sync_to_async
def get_user_object(scope):
    print('1')
    try:
        print('2')
        token_key = parse_qs(scope['query_string'].decode('utf8'))['token'][0]
        print('3')
        token = Token.objects.get(key=token_key)
        print('4')
        return token.user
    except Token.DoesNotExist:
        print('5')
        return AnonymousUser()
    except KeyError:
        print('6')
        return AnonymousUser()
        
        

class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        print('₹++₹'*100)
        AuthTokenMiddlewareInstance(scope, self)

class AuthTokenMiddlewareInstance:
    
    def __init__(self, scope, middleware):
        print('entered in ini methos')
        self.scope = dict(scope)
        self.inner = middleware.inner
    
    async def __call__(self, receive, send):
        print('entered in 2 call func')
        self.scope['user'] = await get_user_object(self.scope)
        inner = self.inner(self.scope)
        return await inner(receive, send)
 
'''

from functools import partial
# For sync websocket use this
@database_sync_to_async
def get_user_object(scope):
    print('here')
    try:
        token_key = parse_qs(scope['query_string'].decode('utf8'))['token'][0]
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
    except KeyError:
        return AnonymousUser()
        
        

class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
      #  scope['user'] = await get_user_object(scope)
        scope['user'] = get_user_object(scope)
        return self.inner(scope)
        
        
'''
# original
class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    scope['user'] = token.user
                    close_old_connections()
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)
'''       


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))