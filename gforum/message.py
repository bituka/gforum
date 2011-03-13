#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import os
import sys
import logging
import datetime

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import gforum.thread
import gforum.forum
import gforum.users

from gforum.models import GForumMessage
from gforum.util   import normalizeMessageText

def checkMessage(msg_text):
    if not msg_text:
        msg_text = ''
    msg_text = msg_text.strip()
    if len(msg_text)==0:
        msg = 'Message cannot be empty'
        logging.error(msg)
        raise ValueError(msg)
    return msg_text

def createNewMessage(forum_key_str, thread_key_str, msg_text, user):
    msg_text = checkMessage(msg_text)
    forum  = gforum.forum.getForumByKey(forum_key_str)
    thread = gforum.thread.getThreadByKey(thread_key_str)
    message = createNewMessageUnchecked(thread, user, msg_text)
    updateThreadForumUserStat(forum, thread, user, message)
    
def createNewMessageUnchecked(thread, user, message_text):
    message = GForumMessage()
    message.text = normalizeMessageText(message_text)
    message.user = user
    message.thread_key = str(thread.key())
    message.put()        
    return message

def updateThreadForumUserStat(forum, thread, user, message):
    gforum.thread.addThreadMessage(thread, message)
    gforum.forum.addMessage(forum, message)
    gforum.users.incrementMessageNumber(user)

def renderMessageJson(message):
    tpl_val = {
        'message'  : message
    }
    tpl_path = os.path.join(os.path.dirname(__file__), 'json/message.json')
    rendered_msg = template.render(tpl_path, tpl_val)
    return rendered_msg

