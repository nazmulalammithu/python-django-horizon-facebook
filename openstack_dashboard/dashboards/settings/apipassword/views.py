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

from horizon import forms

from .forms import ApiPasswordForm
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from horizon.facebook.models import FacebookProfile, ApiPasswordRequest


class ApiPasswordView(forms.ModalFormView):
    form_class = ApiPasswordForm
    template_name = 'settings/apipassword/change.html'
    success_url = reverse_lazy('horizon:settings:apipassword:index')

    def get_context_data(self, **kwargs):
        user = None
        pass_req = None
        password = None
        try:
            user = User.objects.get(username=self.request.user.username)
            try:
                pass_req = ApiPasswordRequest.objects.get(user_id = user.id)
                if pass_req.set_stamp == None:
                    profile = FacebookProfile.objects.get(user=user)
                    password = profile.password
            except:
                pass
        except:
            pass
          
        return {'user': user,
                'pass_req': pass_req,
                'password': password}
