===================
Django-Threaded-Messages
===================

This app is very similar to the Messaging System on Facebook. 

Features:
Each Message is a thread with participants and messages
Inbox with filter for read and unread messages
Outbox
Fulltext search support using Haystack
Users are notified using django-notification when new messages arrive
Batch update to set messages to read/unread/delete
Ajax posting of messages within thread
Can be used with jquery.tokeninput to offer a similar usuability as Facebook when it comes to selecting recipients.
Installable using pip and easy_install 

Dependencies:
Haystack
Django-notification

There are two other repositories doing this (one of them is not maintained anymore):
https://github.com/typeish/django-threaded-messages

I am not sure what the exact differences are to this implementation. I am pretty certain that they don't include read/unread, fulltext search, pip install etc.



