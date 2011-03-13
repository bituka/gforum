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

from models import GForumThread
from models import GForumMessage
from util   import translit

import gforum.forum

def checkThreadTitle(title):
    if not title:
        title = ''
    title = title.strip()
    if len(title)==0:
        msg = 'Wrong thread title'
        logging.error(msg)
        raise ValueError(msg)
    return title

def createNewEmptyThread(forum, title, user):
    title = checkThreadTitle(title)

    thread = GForumThread()
    
    thread.title = title
    thread.permalink   = translit(title)
    thread.messages_number = 0
    thread.views_number    = 1
    thread.message_list    = []
    thread.thread_starter  = user
    thread.forum = forum
    
    thread.put()
    return thread

def addThreadMessage(thread, msg):
    thread.message_list.append(msg.key())
    thread.messages_number = thread.messages_number + 1
    thread.last_message = msg
    thread.put()
    
def createNewThread(forum_key_str, thread_title, message_text, user):
    import gforum.message
    import gforum.users
    forum = gforum.forum.getForumByKey(forum_key_str)
    gforum.message.checkMessage(message_text)
    thread = createNewEmptyThread(forum, thread_title, user)
    message = gforum.message.createNewMessageUnchecked(thread, user, message_text)
    addThreadMessage(thread, message)
    gforum.forum.addForumThreadMessage(forum, thread, message)
    gforum.users.incrementMessageNumber(user)
    return thread

def getThreadByKey(thread_key):
    logging.info('[getThreadByKey] thread_key=%s' % thread_key)
    real_thread_key = None
    real_thread_key = db.Key(thread_key)
    thread = GForumThread.get(real_thread_key)
    if not thread:
        raise ValueError('No forum thread with this key: "%s"' % thread_key)
    return thread

def getAllForumThreads(forum):
    threads = GForumThread.get(forum.thread_list)
    logging.info('[getAllForumThreads] threads.length=%d' % len(threads))
    return threads

def getForumThreads(forum, page, page_size):
    threads = GForumThread.get(forum.thread_list)
    return threads

def getForumThread(tid):
    thread_id = int(tid)
    thread = GForumThread.get_by_id(thread_id)
    if not thread:
        raise ValueError('No thread with such id: "%s"' % tid)
    return thread

def getThreadMessages(thread):
    messages = GForumMessage.get(thread.message_list)
    return messages

def incrementThreadViews(thread):
    thread.views_number = thread.views_number + 1
    thread.put()
