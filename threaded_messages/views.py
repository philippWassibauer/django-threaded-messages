# -*- coding:utf-8 -*-
import datetime

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse
from django.conf import settings

from django_messages.models import *
from django_messages.forms import ComposeForm, ReplyForm


@login_required
def inbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    thread_list = Participant.objects.inbox_for(request.user)
    return render_to_response(template_name, {
        'thread_list': thread_list,
    }, context_instance=RequestContext(request))

@login_required
def outbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of sent messages by the current user.
    Optional arguments:
        ``template_name``: name of the template to use.
    """
    thread_list = Participant.objects.outbox_for(request.user)
    return render_to_response(template_name, {
        'thread_list': thread_list,
    }, context_instance=RequestContext(request))

@login_required
def trash(request, template_name='django_messages/trash.html'):
    """
    Displays a list of deleted messages. 
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    message_list = Participant.objects.trash_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
    }, context_instance=RequestContext(request))

@login_required
def compose(request, recipient=None, form_class=ComposeForm,
        template_name='django_messages/compose.html', success_url=None, recipient_filter=None):
    """
    Displays and handles the ``form_class`` form to compose new messages.
    Required Arguments: None
    Optional Arguments:
        ``recipient``: username of a `django.contrib.auth` User, who should
                       receive the message, optionally multiple usernames
                       could be separated by a '+'
        ``form_class``: the form-class to use
        ``template_name``: the template to use
        ``success_url``: where to redirect after successfull submission
    """
    if request.method == "POST":
        sender = request.user
        form = form_class(data=request.POST, sender=request.user, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save()
            request.user.message_set.create(
                message=_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if request.GET.has_key('next'):
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(sender=request.user)
        if recipient is not None:
            recipients = [u for u in User.objects.filter(username__in=[r.strip() for r in recipient.split('+')])]
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def delete(request, thread_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely. 
    A cron-job should prune the database and remove old messages which are 
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    
    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = datetime.datetime.now()
    thread = get_object_or_404(Thread, id=thread_id)
    user_part = get_object_or_404(Participant, user=user, thread=thread)

    if request.GET.has_key('next'):
        success_url = request.GET['next']
    elif success_url is None:
        success_url = reverse('messages_inbox')
    
    user_part.deleted_at = now
    user_part.save()
    user.message_set.create(message=_(u"Conversation successfully deleted."))
    return HttpResponseRedirect(success_url)


@login_required
def undelete(request, thread_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    thread = get_object_or_404(Thread, id=thread_id)
    user_part = get_object_or_404(Participant, user=user, thread=thread)

    if request.GET.has_key('next'):
        success_url = request.GET['next']
    elif success_url is None:
        success_url = reverse('messages_inbox')

    user_part.deleted_at = now
    user_part.save()
    user.message_set.create(message=_(u"Conversation successfully recovered."))
    return HttpResponseRedirect(success_url)

@login_required
def view(request, thread_id, form_class=ReplyForm,
        success_url=None, recipient_filter=None, template_name='django_messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """    

    user = request.user
    thread = get_object_or_404(Thread, id=thread_id)
  
    """
    Reply stuff
    """
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save(sender=user, thread=thread)
            request.user.message_set.create(
                message=_(u"Reply successfully sent."))
            if success_url is None:
                success_url = reverse('messages_detail', args=(thread.id,))
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()

    now = datetime.datetime.now()
    participant = get_object_or_404(Participant, thread=thread, user=request.user)
    message_list = []
    for message in thread.all_msgs.all():
        unread = True
        if participant.read_at and message.sent_at <= participant.read_at:
            unread = False
        message_list.append((message,unread,))
    participant.read_at = now
    participant.save()
    return render_to_response(template_name, {
        'thread': thread,
        'message_list': message_list,
        'form': form,
    }, context_instance=RequestContext(request))
