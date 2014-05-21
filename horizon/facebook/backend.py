import cgi
import json
import urllib
import logging
import string
import random

from httplib2 import Http
from django.conf import settings
from django.core.urlresolvers import reverse
from keystoneclient.exceptions import Conflict
from keystoneclient.v2_0 import client as keystone_client
from django.contrib import messages
from openstack_auth.backend import KeystoneBackend
from openstack_auth.user import create_user_from_token
from openstack_auth.user import Token
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

class FacebookBackend:
    admin_client = None

    def _admin_client(self):
        if not self.admin_client:
            self.admin_client = keystone_client.Client(
                                    username=settings.ADMIN_USER,
                                    password=settings.ADMIN_PASSWORD,
                                    tenant_name=settings.ADMIN_TENANT,
                                    auth_url=settings.OPENSTACK_KEYSTONE_URL)
        return self.admin_client

    def keystone_get_endpoint(self, service, type='publicurl'):
        service = self._admin_client().services.find(name=service)
        endpoint = self._admin_client().endpoints.find(service_id=service.id)
        return eval('endpoint.%s' % type)


    def keystone_user_exists(self, username):
        keystone_admin = self._admin_client()
        users = keystone_admin.users.list()
        for user in users:
            if user.name == username:
                return True
        return False

    def get_keystone_tenant(self, tenant_name):
        keystone_admin = self._admin_client()
        tenants = keystone_admin.tenants.list()
        for tenant in tenants:
            if tenant.name == tenant_name:
                return tenant
        return None

    def add_keystone_user(self, settings, tenant_name, password, fb_profile):
        keystone_admin = self._admin_client()
    
        tenant = keystone_admin.tenants.create(tenant_name,
                                               "Auto created account",
                                               True)
        user = keystone_admin.users.create(tenant_name,
                                           password,
                                           fb_profile['email'],
                                           tenant.id,
                                           True)
        member_user_role = settings.MEMBER_USER_ROLE
        try:
            keystone_admin.roles.add_user_role(user.id,
                                           member_user_role,
                                           tenant.id)
        except Conflict:
            pass
        return tenant

    def facebook_get_token_profile(self, token, request):
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': request.build_absolute_uri(
                reverse('horizon.facebook.views.authentication_callback')),
            'code': token,
        }
        target = urllib.urlopen(
                'https://graph.facebook.com/oauth/access_token?'
                + urllib.urlencode(args)).read()
        response = cgi.parse_qs(target)
        if 'access_token' not in response:
            return None, None
        access_token = response['access_token'][-1]

        # Read the user's profile information
        fb_profile = urllib.urlopen(
                'https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = json.load(fb_profile)

        return access_token, fb_profile

    def facebook_trystack_group_member(self, access_token):
        try:
            graph_data = None
            group_url = (
                    "https://graph.facebook.com/"
                    "269238013145112/members?limit=1&access_token=%s"
                    % access_token)
            f = urllib.urlopen(group_url)
            graph_data_json = f.read()
            f.close()
            graph_data = json.loads(graph_data_json)

            return (len(graph_data['data']) > 0)
        except:
            return False


    def authenticate(self, token=None, request=None):
        """ Reads in a Facebook code and asks Facebook
            if it's valid and what user it points to. """
        logger.error('test')
        keystone = KeystoneBackend()
        self.keystone = keystone

        # Get a legit access token from Facebook
        access_token, fb_profile = self.facebook_get_token_profile(token, request)
        if not access_token:
            # No access token means failed auth to FB
            msg = _("Facebook login invalid or Token Expired")
            messages.error(request, msg)
            logger.error(msg)
            return None

        facebook_id = fb_profile['id']

        # verify TryStack group membership
        if not self.facebook_trystack_group_member(access_token):
            msg = _("Facebook id %s is not a member of the TryStack Facebook group" % facebook_id)
            messages.error(request, msg)
            logger.error(msg)
            return None

        #### If we got here then auth and group membership are valid
        #### time to ensure the user exists and get a token

        # create user and tenant if they don't exist
        username = tenant_name = "facebook%s" % facebook_id
        password = "".join([random.choice(
                           string.ascii_lowercase + string.digits)
                           for i in range(8)])
        if not self.keystone_user_exists(username):
            tenant = self.add_keystone_user(settings, tenant_name, password, fb_profile)
        else:
            tenant = self.get_keystone_tenant(tenant_name)


        # get a keystone token for the user (requires the custom auth filter)
        d = '{"auth":{"%s": "customer-x", "passwordCredentials": {"username": "%s", "password": "fake_password"}}}' % (username, username)
        url = "%s/tokens/" % self.keystone_get_endpoint('keystone', 'adminurl')
        headers = {'Content-Type': 'application/json; charset=UTF-8', 'X-Auth-Token': settings.ADMIN_TOKEN}
        resp, content = Http().request(uri=url, method="POST", headers=headers, body=d)

        # load the token, create a new client based on the token
        auth_json = json.loads(content)['access']
        client = keystone_client.Client(username=username,
                                        tenant_name=username,
                                        token=auth_json['token']['id'],
                                        auth_url=settings.OPENSTACK_KEYSTONE_URL)
        # use the client and token to create a Token object
        token = Token(auth_ref=client.auth_ref)
        # generate a django user (this is how openstack_auth.backend does it too)
        user = create_user_from_token(request, token, settings.OPENSTACK_KEYSTONE_URL)
                          #client.service_catalog.url_for(endpoint_type='publicURL'))
        return user

    def get_user(self, user_id):
        """ Just returns the user of a given ID. """
        try:
            keystone = KeystoneBackend()
            keystone.request = self.request
        except:
            return None
        return keystone.get_user(user_id)

    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = False
