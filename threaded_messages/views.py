# -*- coding:utf-8 -*-
import datetime
from django.contrib.auth import load_backend, login, BACKEND_SESSION_KEY
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from avatar.templatetags.avatar_tags import avatar_url
from threaded_messages.models import *
from threaded_messages.forms import ComposeForm, ReplyForm
import simplejson
from threaded_messages.models import Thread
import logging


@login_required
def inbox(request, template_name='django_messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    only_read = request.GET.get("only_read", False)
    only_unread = request.GET.get("only_unread", False)
    only_unreplied = request.GET.get("only_unreplied", None)

    read = None
    if only_read:
        read = True
    elif only_unread:
        read = False

    if only_unreplied:
        only_unreplied = True

    thread_list = Participant.objects.inbox_for(request.user, read=read, only_unreplied=only_unreplied)
        
    return render_to_response(template_name, {
        'thread_list': thread_list,
        'only_read': only_read,
        'only_unread': only_unread,
        'only_unreplied': only_unreplied,
    }, context_instance=RequestContext(request))


@login_required
def search(request, template_name="django_messages/search.html"):
    from haystack.query import SearchQuerySet #include here, so the dependency is only needed when used
    search_term = request.GET.get("q")
    results = SearchQuerySet().filter(content=search_term,
                                    participants=request.user.pk)\
                                    .order_by('-last_message').models(Thread)
                    # leads to error in haystack: .order_by("-last_message")
    return render_to_response(template_name, {
                                  "thread_results": results,
                                  "search_term": search_term,
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
    recipients = []
    if request.method == "POST":
        sender = request.user
        form = form_class(data=request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user)
            request.user.message_set.create(
                message=_(u"Message successfully sent."))
            if success_url is None:
                success_url = reverse('messages_inbox')
            if request.GET.has_key('next'):
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
        if recipient is not None:
            recipients = [u for u in User.objects.filter(username__in=[r.strip() for r in recipient.split('+')])]
            form.fields['recipient'].initial = recipients
    return render_to_response(template_name, {
        'form': form,
        'recipients': recipients,
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
    # in this view we want the last message last
    for message in thread.all_msgs.all().order_by("sent_at"):
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
        'participant': participant,
    }, context_instance=RequestContext(request))


@login_required
def batch_update(request, success_url=None):
    """
    Gets an array of message ids which can be either deleted or marked as
    read/unread
    """
    if request.method == "POST":
        ids = request.POST.getlist("batchupdateids")
        if ids:
            threads = Thread.objects.filter(pk__in=ids)
            for thread in threads:
                participant = thread.participants.filter(user=request.user)
                if participant:
                    participant = participant[0]
                    if request.POST.get("action") == "read":
                        participant.read_at = datetime.datetime.now()
                    elif request.POST.get("action") == "delete":
                        participant.deleted_at = datetime.datetime.now()
                    elif request.POST.get("action") == "unread":
                        participant.read_at = None
                    participant.save()
        else:
            raise Http404
        
    else:
        # this should only happen when hacked or developer uses wrong, therefore
        # return simple message
        return HttpResponse("Only Post allowed", code=400)
        
    if success_url:
        return HttpResponseRedirect(success_url)
    else:
        # either go to last page, or to inbox as fallback
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            return HttpResponseRedirect(referer)
        else:
            return HttpResponseRedirect(reverse("messages_inbox"))
            
            

@login_required
def message_ajax_reply(request, thread_id,
                  template_name="django_messages/message_list_view.html"):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.POST:
        form = ReplyForm(request.POST)
        if form.is_valid():
            try:
                (thread, new_message) = form.save(sender=request.user, thread=thread)
            except Exception, e:
                logging.exception(e)
                return HttpResponse(status=500, content="Message could not be sent")
                
            return render_to_response(template_name,{
                "message": new_message,
            }, context_instance=RequestContext(request))
        else:
            return HttpResponse(status=400, content="Invalid Form")


@login_required
def recipient_search(request):
    term = request.GET.get("term")
    users = User.objects.filter(Q(first_name__icontains=term)|
                                Q(last_name__icontains=term)|
                                Q(username__icontains=term)|
                                Q(email__icontains=term))
    if request.GET.get("format") == "json":
        data = []
        for user in users:
            avatar_img_url = avatar_url(user, size=50)
            data.append({"id": user.username,
                         "url": reverse("profile_detail",args=(user.username,)),
                         "name": "%s %s"%(user.first_name, user.last_name),
                         "img": avatar_img_url})

        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/json')
