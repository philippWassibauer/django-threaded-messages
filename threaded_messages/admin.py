from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User, Group
from threaded_messages.models import *


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'sent_at','body')
    
admin.site.register(Message, MessageAdmin)
admin.site.register(Thread)
admin.site.register(Participant)
