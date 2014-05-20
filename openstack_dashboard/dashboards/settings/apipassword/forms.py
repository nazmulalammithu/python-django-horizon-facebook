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

from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import validators
from openstack_dashboard import api

from django.contrib.auth.models import User
from horizon.facebook.models import ApiPasswordRequest
from horizon.facebook.models import FacebookProfile


class ApiPasswordForm(forms.SelfHandlingForm):
    def handle(self, request, data):
        
        user = User.objects.get(username=request.user.username)
        profile = FacebookProfile.objects.get(user=user)
        req, c = ApiPasswordRequest.objects.get_or_create(user=user)
        if not c:
            req.set_stamp = None
            req.save()
        password = "".join([random.choice(
                            string.ascii_uppercase + string.ascii_lowercase + string.digits)
                                   for i in range(16)])

        try:
            api.keystone.user_update_own_password(request,
                                                profile.password,
                                                password)
            profile.password = password
            profile.save() 
            return True

        except Exception, e:
            exceptions.handle(request,
                              _('Unable to change password. %s' % e))
            return False


        return True
