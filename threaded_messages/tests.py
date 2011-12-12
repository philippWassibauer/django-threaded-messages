import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from models import Message
from utils import strip_quotes

        
class UtilsTest(TestCase):
    def test_strip_quotes(self):
        body = """nyan nyan nyan nyan nyan
        nyan nyan nyan nyan nyan
        nyan nyan nyan nyan nyan

        2011/10/28 Nyan Cat <nyan@nyan.cat>:
         > hey guys
        > sarete il 31 dicembre con Pascal a Firenze?
        > lo spero tanto, nel caso ditemi qualcosa...
        >
        >>>
        >
        >>
        >"""
        
        body_stripped = """nyan nyan nyan nyan nyan
        nyan nyan nyan nyan nyan
        nyan nyan nyan nyan nyan
        """
        
        self.assertEquals(body_stripped.strip(), strip_quotes(body).strip())