import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.contrib.auth.models import User

from threaded_messages.models import *
from threaded_messages.fields import CommaSeparatedUserField

notification = None
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    
class ComposeForm(forms.Form):
    """
    A simple default form for private messages.
    """
    recipient = CommaSeparatedUserField(label=_(u"Recipient"))
    subject = forms.CharField(label=_(u"Subject"))
    body = forms.CharField(label=_(u"Body"),
        widget=forms.Textarea(attrs={'rows': '12', 'cols':'55'}))
    
    def __init__(self, *args, **kwargs):
        recipient_filter = kwargs.pop('recipient_filter', None)
        super(ComposeForm, self).__init__(*args, **kwargs)
        if recipient_filter is not None:
            self.fields['recipient']._recipient_filter = recipient_filter
    
    def save(self, sender):
        recipients = self.cleaned_data['recipient']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        
        new_message = Message.objects.create(body=body, sender=sender)
        
        thread = Thread.objects.create(subject=subject,
                                       latest_msg=new_message)
        thread.all_msgs.add(new_message)
        thread.save()

        for recipient in recipients:
            Participant.objects.create(thread=thread, user=recipient)
        
        (sender_part, created) = Participant.objects.get_or_create(thread=thread, user=sender)
        sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
        sender_part.save()
        
        #send notifications
        if notification:
            notification.send(recipients, "received_email", 
                                        {"thread": thread,
                                         "message": new_message}, sender=sender)
        
        return (thread, new_message)


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
        
        recipients = []
        for participant in thread.participants.all():
            participant.deleted_at = None
            participant.save()
            if sender != participant.user: # dont send emails to the sender!
                recipients.append(participant.user)
        
        sender_part = Participant.objects.get(thread=thread, user=sender)
        sender_part.replied_at = sender_part.read_at = datetime.datetime.now()
        sender_part.save()
        
        if notification:
            notification.send(recipients, "received_email", 
                                        {"thread": thread,
                                         "message": new_message}, sender=sender)
            
        return (thread, new_message)
