#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

from gforum.apiv1 import GForumApiv1DispatcherPage
from gforum.admin import GForumAdminPage
from gforum.forum import getAllForums
from gforum.forum import getForum
from gforum.forum import getAllForumThreads
from gforum.thread import getThreadMessages
from gforum.thread import getForumThread
from gforum.thread import incrementThreadViews

gforum_root  = '/forum'
gforum_theme = 'default'
gforum_threads_per_page  = 20
gforum_messages_per_page = 20

class GForumSitemapPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write('<lala>sitemap here</lala>')
            
class GForumDispatcherPage(webapp.RequestHandler):

    def get(self):
        gforum_entity_path = self.request.url[self.request.url.rfind(gforum_root)+1+len(gforum_root):]
        idx1 = gforum_entity_path.find('/')
        # if url is like: '/forum' or '/forum/'
        if len(gforum_entity_path)==0:
            self.showForumList() 
        # if url is like: '/forum/forum1' or '/forum/php_forum'
        elif idx1==-1:
            self.showSpecificForum(gforum_entity_path)
        # if url is like: '/forum/forum1/234/thread1_title' 
        else:
            forum_url = gforum_entity_path[:idx1]
            thread_id = gforum_entity_path[idx1+1: gforum_entity_path.find('/', idx1+1)]
            #self.response.out.write('<h1>Forum ID: '+forum_url+'</h1>')
            #self.response.out.write('<h1>Thread ID: '+thread_id+'</h1>')
            self.showSpecificThread(forum_url, thread_id)
    
    def showForumList(self):
        forums = getAllForums()

        has_forums = len(forums)>0
        
        template_values = {
            'forumpath'  : gforum_root,
            'has_forums' : has_forums,
            'forums'     : forums
        }
        template_path = 'themes/%s/main_list_forums.html' % gforum_theme
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, template_values).decode('utf-8'))

    def showSpecificForum(self, url):
        forum = getForum(url)
        if not forum:
            self.redirect(gforum_root)
            return

        has_threads = len(forum.thread_list)>0

        # here handle page number and number of records per page
        # params: page = 1
        #         page_size = 20

        threads = []
        if len(forum.thread_list)>0:
            threads = getAllForumThreads(forum)

        logging.info('[main] threads.length = %d' % len(threads))
        template_values = {
            'has_threads': has_threads,
            'forumpath'  : gforum_root,
            'forum': forum,
            'threads' : threads
        }
        template_path = 'themes/%s/forum_list_threads.html' % gforum_theme
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, template_values).decode('utf-8'))

    def showSpecificThread(self, forum_url, thread_id):
        forum = getForum(forum_url)
        if not forum:
            self.redirect(gforum_root)
            return
        thread   = getForumThread(thread_id)
        messages = getThreadMessages(thread)

        # thread should have at least one message
        #has_messages = len(messages)>0

        # here handle page number and number of records per page
        # params: page = 1
        #         page_size = 20

        template_values = {
            'forumpath'  : gforum_root,
            'forum': forum,
            'thread' : thread,
            'messages' : messages
        }
        template_path = 'themes/%s/thread_list_messages.html' % gforum_theme
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, template_values).decode('utf-8'))
        incrementThreadViews(thread)


        
application = webapp.WSGIApplication([
  (format('%s/sitemap.xml' % gforum_root), GForumSitemapPage),
  (format('%s/admin.*'     % gforum_root), GForumAdminPage),
  (format('%s/api/v1/.*'   % gforum_root), GForumApiv1DispatcherPage),
  (format('%s.*'           % gforum_root), GForumDispatcherPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
