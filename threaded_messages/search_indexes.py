import datetime
from haystack.indexes import *
from haystack import site
from models import Thread

class ThreadIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    participants = MultiValueField()
    last_message = DateTimeField(model_attr='latest_msg__sent_at')

    def get_queryset(self):
        return Thread.objects.all()
    
    def prepare_participants(self, object):
        return [p.user.pk for p in object.participants.all()]
        
site.register(Thread, ThreadIndex)