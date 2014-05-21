import logging
import json
 
from keystone.common import wsgi
from keystone import exception
from keystone.common import config

AUTH_TOKEN_HEADER = 'X-Auth-Token'

# Environment variable used to pass the request context
CONTEXT_ENV = wsgi.CONTEXT_ENV

CONF = config.CONF

class ServiceTokenMiddleware(wsgi.Middleware):
    def __init__(self, *args, **kwargs):
        super(ServiceTokenMiddleware, self).__init__(*args, **kwargs)

    def process_request(self, request):
        if request.environ.get('REMOTE_USER', None) is not None:
            # Assume that it is authenticated upstream
            return self.application

        token = request.headers.get(AUTH_TOKEN_HEADER)
        context = request.environ.get(CONTEXT_ENV, {})

        if token == CONF.admin_token:
            try:
                body = json.loads(request.body)
                username = body['auth']['passwordCredentials']['username']
                if username is None:
                    raise exception.Unauthorized("Invalid user")
                request.environ['REMOTE_USER'] = username
            except:
                pass
