from django.conf import settings

THREADED_MESSAGES_USE_SENDGRID = getattr(settings, 'THREADED_MESSAGES_USE_SENDGRID', False)
THREADED_MESSAGES_ID = getattr(settings, 'THREADED_MESSAGES_ID', 'm')