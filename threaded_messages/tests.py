import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from threaded_messages.models import Message

class DeleteTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user3', 'user3@example.com', '123456')
        self.user2 = User.objects.create_user('user4', 'user4@example.com', '123456')
        self.msg1 = Message(sender=self.user1, thread=thread, body='Body Text 1')
        self.msg2 = Message(sender=self.user1, thread=thread,  body='Body Text 2')
        self.msg1.sender_deleted_at = datetime.datetime.now()
        self.msg2.recipient_deleted_at = datetime.datetime.now()
        self.msg1.save()
        self.msg2.save()
                
   