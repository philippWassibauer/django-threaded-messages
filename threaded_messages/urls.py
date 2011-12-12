from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from threaded_messages.views import *

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^search/$', search, name='messages_search'),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^compose/$', compose, name='messages_compose'),
    url(r'^compose/(?P<recipient>[\+\w]+)/$', compose, name='messages_compose_to'),
    url(r'^view/(?P<thread_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<thread_id>[\d]+)/$', delete, name='messages_delete'),
    url(r'^undelete/(?P<thread_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^batch-update/$', batch_update, name='messages_batch_update'),
    url(r'^trash/$', trash, name='messages_trash'),
    
    url(r"^recipient-search/$", recipient_search, name="recipient_search"),
    url(r'^message-reply/(?P<thread_id>[\d]+)/$', message_ajax_reply, name="message_reply"),
    
    # modal composing 
    url(r'^modal-compose/(?P<recipient>[\w.+-_]+)/$', compose, {
                            "template_name":"django_messages/modal_compose.html",
                            "form_class": ComposeForm
                        }, name='modal_messages_compose_to'),
    
    url(r'^modal-compose/$', compose, {
                            "template_name":"django_messages/modal_compose.html",
                            "form_class": ComposeForm
                        }, name='modal_messages_compose'),
)
