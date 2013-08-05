import json, urllib

from django.db import models
from django.contrib.auth.models import User


class FacebookProfile(models.Model):
    user = models.OneToOneField(User)
    facebook_id = models.BigIntegerField()
    access_token = models.CharField(max_length=255)
    password =  models.CharField(max_length=150)
    tenant_id = models.CharField(max_length=150)
    def get_facebook_profile(self):
        fb_profile = urllib.urlopen('https://graph.facebook.com/me?access_token=%s' % self.access_token)
        return json.load(fb_profile)

class ApiPasswordRequest(models.Model):
    user = models.OneToOneField(User)
    create_stamp = models.DateField(auto_now_add=True)
    set_stamp = models.DateField(null=True, blank=True)
