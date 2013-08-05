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

from django import http
from django.core.urlresolvers import reverse

from mox import IsA

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test


INDEX_URL = reverse('horizon:settings:apipassword:index')


class ApiPasswordTests(test.TestCase):

    @test.create_stubs({api.keystone: ('user_update_own_password', )})
    def test_api_password(self):
        self.mox.ReplayAll()

        formData = {'method': 'ApiPasswordForm',}

        res = self.client.post(INDEX_URL, formData)

        self.assertNoFormErrors(res)
