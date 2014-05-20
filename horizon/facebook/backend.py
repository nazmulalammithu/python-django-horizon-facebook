import cgi
import datetime
import json
import os
import urllib

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import reverse
from django.db import IntegrityError
import string
import random
from models import FacebookProfile
from keystoneclient import service_catalog
from keystoneclient.v2_0 import client as keystone_client
from keystoneclient.v2_0 import tokens
from django.contrib import messages
from openstack_auth.backend import KeystoneBackend
from django.utils.translation import ugettext_lazy as _

class FacebookBackend:
    def _admin_client(self):
        return  keystone_client.Client(username=settings.ADMIN_USER,
                                      password=settings.ADMIN_PASSWORD,
                                      tenant_name=settings.ADMIN_TENANT,
                                      auth_url=settings.OPENSTACK_KEYSTONE_URL)

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
        keystone_admin.roles.add_user_role(user.id,
                                           member_user_role,
                                           tenant.id)
        return tenant

    def authenticate(self, token=None, request=None):
        """ Reads in a Facebook code and asks Facebook
            if it's valid and what user it points to. """
        keystone = KeystoneBackend()
        self.keystone = keystone
        args = {
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'redirect_uri': request.build_absolute_uri(
                reverse('horizon.facebook.views.authentication_callback')),
            'code': token,
        }
        # Get a legit access token
        target = urllib.urlopen(
                'https://graph.facebook.com/oauth/access_token?'
                + urllib.urlencode(args)).read()
        response = cgi.parse_qs(target)
        if 'access_token' not in response:
            messages.error(
                request, _("Token Expired, please login again."))
            return None
        access_token = response['access_token'][-1]

        # Read the user's profile information
        fb_profile = urllib.urlopen(
                'https://graph.facebook.com/me?access_token=%s' % access_token)
        fb_profile = json.load(fb_profile)
        tenant_id = None
        password = ""
        try:
            # Try and find existing user
            fb_user = FacebookProfile.objects.get(facebook_id=fb_profile['id'])
            user = fb_user.user
            # Update access_token
            fb_user.access_token = access_token
            password = fb_user.password
            tenant_id = fb_user.tenant_id
            fb_user.save()
        except FacebookProfile.DoesNotExist:
            # No existing user
            try:
                facebook_id = fb_profile['id']
                username = "facebook%s" % facebook_id
                try:
                    user = User.objects.create_user(username, fb_profile['email'])
                except IntegrityError:
                    # Username already exists, make it unique
                    existing_user = User.objects.get(username=username)
                    existing_user.delete()
                    user = User.objects.create_user(username, fb_profile['email'])
                user.save()

                password = "".join([random.choice(
                                        string.ascii_lowercase + string.digits)
                                   for i in range(8)])
                # Create the FacebookProfile
                fb_user = FacebookProfile(user=user, facebook_id=fb_profile['id'],
                                          access_token=access_token,
                                          password=password)
                tenant_name = "facebook%s" % fb_profile['id']
                if not self.keystone_user_exists(username):
                    tenant = self.add_keystone_user(settings, tenant_name, password, fb_profile)
                else:
                    tenant = self.get_keystone_tenant(tenant_name)
                fb_user.tenant_id = tenant.id
                tenant_id = fb_user.tenant_id
                fb_user.save()
            except Exception, e:
                messages.error(request, e)
                if fb_user.id :
                    fb_user.delete()	

        facebook_id = fb_profile['id']
        username = "facebook%s" % facebook_id
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

            if len(graph_data['data']) > 0:
                try:
                    user = keystone.authenticate(request=request,
                                      username=username,
                                      password=password,
                                      auth_url=settings.OPENSTACK_KEYSTONE_URL)
                except Exception, e:
                    messages.error(request, self.keystone_user_exists(username))
                    if not self.keystone_user_exists(username):
                        
                        tenant = self.add_keystone_user(settings, username, password, fb_profile)
                        user = keystone.authenticate(request=request,
                                      username=username,
                                      password=password,
                                      auth_url=settings.OPENSTACK_KEYSTONE_URL)
                    else:
                        raise e
                return user
            else:
                messages.error(
                    request, "Your facebookID is not in TryStack group yet.")
        except Exception as e:
            messages.error(
                request, _("Failed to login facebookID %s") % username)
            messages.error(
                request, _("Failed to login facebookID %s") % e)

    def get_user(self, user_id):
        """ Just returns the user of a given ID. """
        keystone = KeystoneBackend()
        keystone.request = self.request
        return keystone.get_user(user_id)

    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = False
