===============
Django-Threaded-Messages
===============

This app is very similar to the Messaging System on Facebook.
There are tests, but they are from the project I forked it from. I will update and improve them once I get around to it.

Features
===============
* Each Message is a thread with participants and messages
* Inbox with filter for read and unread messages
* Outbox
* Fulltext search support using Haystack
* Users are notified using django-notification when new messages arrive
* Batch update to set messages to read/unread/delete
* Ajax posting of messages within thread
* Can be used with jquery.tokeninput to offer a similar usuability as Facebook when it comes to selecting recipients.
* Installable using pip and easy_install
* Modular message sending using facebox


User Search
===============
The app comes with a very basic user search component. If you want to extend it or adapt it to your needs
look at views.recipient_search. Adapt your own version in a seperate app and then
change the call in your compose templates::
    $("#id_recipient").tokenInput("{% url recipient_search %}?format=json", parameters)

to point to your custom view.


Sendgrid Parse Api Integration for email replies (beta)
===============
This feature is not finished yet. In the future it is possible to enable
reply emails (if you are using Sendgrid as email service) using the following settings::
    THREADED_MESSAGES_USE_SENDGRID = True
    THREADED_MESSAGES_ID = "m"

When a user replies online the recipient will get an email to which he can respond.


Dependencies
===============
* Haystack
* Django-notification
* django-avatar
* django-pagination
* django-uni-form
* sendgrid-parse-api (released soon) - only if email replies should be activated

Install
===============
pip install -e http://github.com/philippWassibauer/django-threaded-messages.git#egg=threaded-messages

or

pip install django-threaded-messages


Similar Projects
===============

There are two other repositories doing this (one of them is not maintained anymore):

https://github.com/typeish/django-threaded-messages

I am not sure what the exact differences are to this implementation. I am pretty certain that they don't include read/unread, fulltext search, pip install etc.


Follow Me
===============
http://github.com/philippWassibauer
http://twitter.com/scalar
http://philippw.tumblr.com
https://bitbucket.org/philippwassibauer


