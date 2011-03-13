#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from google.appengine.api import urlfetch
import gforum.util

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

from gforum.admin import GForumAdminPage
from gforum.forum import getAllForums
from gforum.forum import getForum
from gforum.forum import getAllForumThreads
from gforum.thread import getThreadMessages
from gforum.thread import getForumThread
from gforum.thread import incrementThreadViews

import gforum.settings
import gforum.users

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
view_root    = '%s/view' % gforum_root
gforum_theme = gforum.settings.GFORUM_THEME
gforum_threads_per_page  = gforum.settings.GFORUM_THREADS_PER_PAGE
gforum_messages_per_page = gforum.settings.GFORUM_MESSAGES_PER_PAGE

class GForumRedirectPage(webapp.RequestHandler):
    def get(self):
        self.redirect(view_root)


class GForumDispatcherPage(webapp.RequestHandler):

    def get(self):
        gforum_entity_path = self.request.url[self.request.url.rfind(view_root)+1+len(view_root):]
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

    def getDefaultTemplateData(self):
        user = gforum.users.getAuthorizedUser(self.request, self.response)
        logging.info('[getDefaultTemplateData] user=%s' % user)
        user_authorized = True if user else False
        logging.info('user=%s' % user)
        user.avatar_url = gforum.users.getAvatarUrl(user, gforum_root)
        
        template_values = {
            'user_authorized' : user_authorized,
            'user'            : user,
            'forumpath'       : gforum_root,
            'host'            : '%s://%s' % (self.request.scheme, self.request.host)
        }
        return template_values


    def showForumList(self):
        forums = getAllForums()

        has_forums = len(forums)>0

        template_values = gforum.util.getDefaultTemplateData(self.request, self.response, gforum_root)
        
        template_values['has_forums'] = has_forums
        template_values['forums']     = forums

        template_path = 'themes/%s/main.html' % gforum_theme
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

        template_values = gforum.util.getDefaultTemplateData(self.request, self.response, gforum_root)
        template_values['has_threads'] = has_threads
        template_values['forum']    = forum
        template_values['threads']  = threads

        template_path = 'themes/%s/forum.html' % gforum_theme
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
        
        messagesData = []
        i = 1
        for m in messages:
            t = {
                'message' : m,
                'counter' : i 
            }
            messagesData.append(t)
            i = i+1

        template_values = gforum.util.getDefaultTemplateData(self.request, self.response, gforum_root)
        template_values['thread']   = thread
        template_values['forum']    = forum
        template_values['messages'] = messages
        #template_values['messages']  = messagesData

        template_path = 'themes/%s/thread.html' % gforum_theme
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, template_values).decode('utf-8'))
        incrementThreadViews(thread)


        
application = webapp.WSGIApplication([
  #(format('%s' % gforum_root),  GForumRedirectPage),
  #(format('%s/' % gforum_root), GForumRedirectPage),
  #(format('%s/view.*' % gforum_root), GForumDispatcherPage)
  ('%s' % gforum_root,  GForumRedirectPage),
  ('%s/' % gforum_root, GForumRedirectPage),
  ('%s/view.*' % gforum_root, GForumDispatcherPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
