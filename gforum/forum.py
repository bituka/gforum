#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import os
import sys
import logging
import datetime

from models import GForum
from models import GForumStatistics
from models import GForumOptions
from models import GForumThread
from util   import translit

from gforum.util   import normalizeMessageText

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

def createNewForum(name, permalink, description, options):
    if not name or len(name)==0:
        msg = 'Wrong forum name'
        logging.error(msg)
        raise ValueError(msg)

    if not permalink:
        permalink = ''
    
    permalink = permalink.strip().lower()

    if len(permalink)==0:
        permalink = None
        
    if not permalink:
        permalink = translit(name).lower()
    else:
        permalink = permalink.lower()

    if name.find('/')>=0:
        msg = 'Wrong forum name: forum name cannot contain \'/\' symbol'
        logging.error(msg)
        raise ValueError(msg)

    if permalink =='admin' or permalink =='api':
        msg = 'Wrong forum permalink: cannot be equal to \'admin\' or \'api\''
        logging.error(msg)
        raise ValueError(msg)

    if not description:
        description = ''
    description = description.strip()
    if len(description)==0:
        description = None
    if description:
        description = normalizeMessageText(description)


    forums = GForum.all().filter('permalink =',permalink).fetch(limit=1)
    if len(forums)>0:
        msg = 'Forum with permalink \'%s\' already exist' % permalink
        logging.error(msg)
        raise ValueError(msg)
    
    stat = GForumStatistics()

    forum = GForum()
    forum.name = name
    forum.permalink = permalink
    forum.description = description
    forum.thread_list = []
    forum.messages_number = 0
    forum.threads_number = 0
    forum.put()
    return forum

def renderForumJson(forum):
    tpl_val = {
        'forum'  : forum
    }
    tpl_path = os.path.join(os.path.dirname(__file__), 'json/forum.json')
    rendered_msg = template.render(tpl_path, tpl_val)
    return rendered_msg

def getAllForums():
    forums = GForum.all().order('name').fetch(limit=100)
    return forums


def getForum(permalink):
    forums = GForum.all().filter('permalink =',permalink).fetch(limit=1)
    if len(forums)>0:
        return forums[0]
    else:
        return None

def getForumByKey(forum_key_str):
    key = db.Key(forum_key_str)
    return GForum.get(key)

def getAllForumThreads(forum):
    threads = GForumThread.get(forum.thread_list)
    return threads

def getForumThreads(forum, page, page_size):
    threads = GForumThread.get(forum.thread_list)
    return threads

def addMessage(forum, message):
    forum.last_message = message
    forum.messages_number = forum.messages_number + 1
    forum.put()

def updateForumStatistics(forum_key):
    key = db.Key(forum_key)
    forum = GForum.get(key)
    threads_number = len(forum.thread_list)
    msg_number = 0
    threads = GForumThread.get(forum.thread_list)
    for t in threads:
        msg_number = msg_number + len(t.message_list)
    forum.messages_number = msg_number
    forum.put()

def addForumThreadMessage(forum, thread, message):
    forum.thread_list.append(thread.key());
    forum.threads_number  = forum.threads_number+1
    forum.messages_number = forum.messages_number+1
    forum.last_message = message
    forum.put()

