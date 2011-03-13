#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from gforum.forum   import createNewForum
from gforum.forum   import renderForumJson
from gforum.message import createNewMessage
from gforum.message import renderMessageJson
from gforum.util    import writeApiResponse
from gforum.thread  import createNewThread

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

gforum_root  = '/forum'
api_root     = format('%s/api/v1/' % gforum_root)

class GForumApiv1DispatcherPage(webapp.RequestHandler):
    def get(self):
        self.handler()
    
    def post(self):
        self.handler()

    def handler(self):
        api_method = self.request.url[self.request.url.rfind(api_root)+len(api_root):]  
        if api_method.find('?')>-1:
            api_method = api_method[:api_method.find('?')]
        logging.info('[GForumApiv1DispatcherPage.handler]api_method="%s"' % (api_method))  
        func = API_HANDLERS[api_method]
        func(self.request, self.response)


def message_create(request, response):
    logging.info('[message_create]')
    forum_key  = request.get('forum_key')
    thread_key = request.get('thread_key')
    message_text = request.get('message_text')
    logging.info('[message_create] forum_key=%s' % forum_key)
    logging.info('[message_create] thread_key=%s' % thread_key)
    logging.info('[message_create] message_text=%s' % message_text)
    logging.info('[message_create] going call gforum.message.createNewMessage')
    msg = createNewMessage(forum_key, thread_key, message_text)
    logging.info('[message_create] going call gforum.message.renderMessageJson')
    rendered_message = renderMessageJson(msg)
    logging.info('[message_create] going call gforum.util.writeApiResponse')
    writeApiResponse(response, 'ok', 'ok', rendered_message)
    
def forum_create(request, response):
    if not users.is_current_user_admin():
        writeApiResponse(response, 'fail', 'you are not admin', '')
        return

    try:
        logging.info('[forum_create]')
        forum_name  = request.get('forum_name')
        forum_permalink = request.get('forum_permalink').lower()
        forum_description = request.get('forum_description')
        logging.info('[forum_create] forum_name=%s' % forum_name)
        logging.info('[forum_create] forum_permalink=%s' % forum_permalink)
        logging.info('[forum_create] forum_description=%s' % forum_description)
        forum = createNewForum(forum_name, forum_permalink, forum_description, None)
        rendered_forum = renderForumJson(forum)
        writeApiResponse(response, 'ok', 'ok', rendered_forum)
    except ValueError as va:
        writeApiResponse(response, 'fail', str(va), '')


def thread_create(request, response):
    logging.info('[thread_create]')
    try:
        forum_key    = request.get('forum_key')
        thread_title = request.get('thread_title')
        message_text = request.get('message_text')
        logging.info('[thread_create] forum_key=\'%s\'' % forum_key)
        logging.info('[thread_create] thread_title=\'%s\'' % thread_title)
        logging.info('[thread_create] message_text=\'%s\'' % message_text)
        thread = createNewThread(forum_key, thread_title, message_text)
        #rendered_forum = renderForumJson(forum)
        writeApiResponse(response, 'ok', 'ok', '"fuck"')
    except ValueError as va:
        msg = str(va)
        logging.error('[thread_create] error: ' + msg)
        writeApiResponse(response, 'fail', msg, '')
    

API_HANDLERS = {
    'post_message' :  message_create,
    'create_thread':  thread_create,
    'create_forum' :  forum_create
}


application = webapp.WSGIApplication([
  (format('%s/api/v1/.*'   % gforum_root), GForumApiv1DispatcherPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
