from django.utils.html import strip_tags
import settings as sendgrid_settings
import logging
logger = logging.getLogger('gidsy.apps.sendgrid')

if sendgrid_settings.THREADED_MESSAGES_USE_SENDGRID:
    from sendgrid_parse_api.signals import email_received
else:
    email_received = None

def signal_received_email(sender, sma, app_id, html, text, from_field, **kwargs):
    from utils import reply_to_thread, strip_quotes # circular dependency fix
    logger.debug("Sendgrid signal receive: %s, %s, %s, %s, %s, %s"%(sender, sma, app_id,
                                                                    html, text, from_field) )
    if app_id == sendgrid_settings.THREADED_MESSAGES_ID:
        body =''

        if text:
            body = text

        if not body:
            body = strip_tags(html)

        if body:
            strip_quotes(body)
            thread = sma.content_object
            reply_to_thread(thread, sma.user, body)

def start_listening():
    if email_received:
        logger.debug("Sendgrid start listening")
        email_received.connect(signal_received_email, dispatch_uid="thm_reply")
