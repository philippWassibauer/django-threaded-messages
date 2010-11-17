from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User, Group

from threaded_messages.models import *

admin.site.register(Message)
admin.site.register(Thread)
admin.site.register(Participant)
