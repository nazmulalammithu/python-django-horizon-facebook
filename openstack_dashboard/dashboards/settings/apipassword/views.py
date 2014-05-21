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

from datetime import datetime

from horizon import forms

from .forms import ApiPasswordForm
from django.core.urlresolvers import reverse_lazy
from django.contrib import auth
from django.contrib.auth.models import User
from horizon.facebook.models import FacebookProfile, ApiPasswordRequest


class ApiPasswordView(forms.ModalFormView):
    form_class = ApiPasswordForm
    template_name = 'settings/apipassword/change.html'
    success_url = reverse_lazy('horizon:settings:apipassword:index')

    def get_context_data(self, **kwargs):
        user = None
        password = None
        if 'password' in self.request.session:
            password = self.request.session['password']
            self.request.session.set_expiry(3)

        return {'user': user,
                'password': password}
