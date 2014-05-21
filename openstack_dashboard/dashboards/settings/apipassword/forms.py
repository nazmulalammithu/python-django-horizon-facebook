# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Centrin Data Systems Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import random
import string

from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.views.decorators.debug import sensitive_variables
from django.conf import settings

from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import validators
from openstack_dashboard import api

from keystoneclient.v2_0 import client as keystone_client


class ApiPasswordForm(forms.SelfHandlingForm):
    def handle(self, request, data):
        
        password = "".join([random.choice(
                            string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                   for i in range(16)])

        try:
            client = keystone_client.Client(
                                    username=settings.ADMIN_USER,
                                    password=settings.ADMIN_PASSWORD,
                                    tenant_name=settings.ADMIN_TENANT,
                                    auth_url=settings.OPENSTACK_KEYSTONE_URL)
             
            client.users.update_password(request.user.id, password)
            request.session['password'] = password

        except Exception, e:
            exceptions.handle(request,
                              _('Unable to change password. %s' % e))
            return False


        return True
