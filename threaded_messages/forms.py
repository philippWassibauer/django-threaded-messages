import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User

from django_messages.models import *
from django_messages.fields import CommaSeparatedUserField

from profiles.models import Profile


def get_associated_profiles(user):
    choices = [('', 'User: %s' % user.username)]
    for artist in user.artists.all():
        choices.append((artist.id, 'Artist: %s' % artist.name))
    for venue in user.venues.all():
        choices.append((venue.id, 'Venue: %s' % venue.name))
    return choices

class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    sender_profile = forms.ChoiceField(required=False, label=(u"Associated Profile"))
    
    def __init__(self, sender, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter
        self.sender = sender
        self.fields['sender_profile'].choices = get_associated_profiles(sender)
    
    def save(self):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        sender_profile = None
        if self.cleaned_data['sender_profile'] != u"":
            sender_profile = Profile.objects.get(pk=int(self.cleaned_data['sender_profile']))
        
        new_message = Message.objects.create(body=body, sender=self.sender)
        
        thread = Thread.objects.create(subject=subject,
                                       latest_msg=new_message)
        thread.all_msgs.add(new_message)
        thread.save()

        for recipient in recipients:
            Participant.objects.create(thread=thread, user=recipient)
        
        (sender_part, created) = Participant.objects.get_or_create(thread=thread, sender_profile=sender_profile, user=self.sender)
        sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
        sender_part.save()
        
        return thread

class ReplyForm(forms.Form):
    """
    A simple default form for private messages.
    """
    body = forms.CharField(label=_(u"Reply"),
        widget=forms.Textarea(attrs={'rows': '4', 'cols':'55'}))
    
    def save(self, sender, thread):
        body = self.cleaned_data['body']
        
        new_message = Message.objects.create(body=body, sender=sender)
        new_message.parent_msg = thread.latest_msg
        thread.latest_msg = new_message
        thread.all_msgs.add(new_message)
        thread.save()
        new_message.save()
        
        for participant in thread.participants.all():
            participant.deleted_at = None
            participant.save()
        
        sender_part = Participant.objects.get(thread=thread, user=sender)
        sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
        sender_part.save()
        
        return thread
