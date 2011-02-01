from django.conf import settings
from django.utils.translation import ugettext_noop as _
from django.db.models import signals

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("received_email", _("Received a Message"), _("Someone has sent you a message"))
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes (Threaded Messages) as notification app not found"