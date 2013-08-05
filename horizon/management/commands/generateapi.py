from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from keystoneclient.v2_0 import client as keystone_client
from horizon.facebook.models import ApiPasswordRequest
from horizon.facebook.models import FacebookProfile
from django.contrib.auth.models import User

from optparse import make_option

class Command(BaseCommand):
    #args = '[user]'
    #help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        if len(args):
            for u in args:
                user = User.objects.get(username=u)
                req = ApiPasswordRequest.objects.get(user=user)
                req.set_stamp = datetime.now()
                req.save()
        else:
            reqs = ApiPasswordRequest.objects.filter(set_stamp=None)
            for req in reqs:
                profile = FacebookProfile.objects.get(user=req.user)
                print '%s:%s' % (req.user.username, profile.password)
