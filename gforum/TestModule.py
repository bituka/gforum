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
from util   import genRandomSymbols
from forum  import createNewForum

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template


def createForums():

    for i in range(5):
        createNewForum('myforum %d' % (i+1),None,None,)

        forum = new GForum()
        forum.name = 'myforum %d' % (i+1)
        forum.url  = genRandomSymbols(10)
        forum.options = opt
        forum.statistics = stat
        forum.put()


