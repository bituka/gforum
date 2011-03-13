#!/usr/bin/env python
#

import re
import sys
import os
import logging
import wsgiref.handlers

import gforum.util
import gforum.users 

from gforum.forum   import createNewForum
from gforum.forum   import renderForumJson
from gforum.message import createNewMessage
from gforum.message import renderMessageJson
import gforum.thread

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

import gforum.settings

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
api_root     = '%s/api/v1/' % gforum_root

class PostMessageApi(webapp.RequestHandler):
    
    def post(self):
        self.handler()

    def handler(self):
        logging.info('[PostMessageApi]')
        request = self.request
        response = self.response
        try: 
            user = gforum.users.getAuthorizedUser(request, response)
            if not user:        
                gforum.util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to post messages', 'null')
                return
            forum_key  = request.get('forum_key')
            thread_key = request.get('thread_key')
            message_text = request.get('message_text')
            msg = createNewMessage(forum_key, thread_key, message_text, user)
            rendered_message = renderMessageJson(msg)
            gforum.util.writeApiResponse(response, 'ok', 'ok', rendered_message)
        except:
            gforum.util.writeApiResponse(response, 'fail', 'Error occured', 'null')


class CreateForumApi(webapp.RequestHandler):
    def post(self):
        self.handler()

    def handler(self):
        request = self.request
        response = self.response
        
        try:
            if not users.is_current_user_admin():
                gforum.util.writeApiResponse(response, 'fail', 'you are not admin', '')
                return
            logging.info('[forum_create]')
            forum_name  = request.get('forum_name')
            forum_permalink = request.get('forum_permalink').lower()
            forum_description = request.get('forum_description')
            logging.info('[forum_create] forum_name=%s' % forum_name)
            logging.info('[forum_create] forum_permalink=%s' % forum_permalink)
            logging.info('[forum_create] forum_description=%s' % forum_description)
            forum = createNewForum(forum_name, forum_permalink, forum_description, None)
            rendered_forum = renderForumJson(forum)
            gforum.util.writeApiResponse(response, 'ok', 'ok', rendered_forum)
        except ValueError:
            #gforum.util.writeApiResponse(response, 'fail', str(va), '')
            msg = 'Wrong value!'
            logging.error('[CreateForumApi] error: ' + msg)
            gforum.util.writeApiResponse(response, 'fail', msg, 'null')
        except:
            gforum.util.writeApiResponse(response, 'fail', 'Error occured', 'null')


class CreateThreadApi(webapp.RequestHandler):
    def post(self):
        self.handler()

    def handler(self):
        request = self.request
        response = self.response
        logging.info('[CreateThreadApi]')
        try:
            user = gforum.users.getAuthorizedUser(request, response)
            if not user:
                gforum.util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to create threads', 'null')
                return
            forum_key    = request.get('forum_key')
            thread_title = request.get('thread_title')
            message_text = request.get('message_text')
            thread = gforum.thread.createNewThread(forum_key, thread_title, message_text, user)
            #rendered_forum = renderForumJson(forum)
            gforum.util.writeApiResponse(response, 'ok', 'ok', '"fuck"')
        except ValueError:
            #msg = str(va)
            msg = 'Wrong value!'
            logging.error('[CreateThreadApi] error: ' + msg)
            gforum.util.writeApiResponse(response, 'fail', msg, '')
        except:
            gforum.util.writeApiResponse(response, 'fail', 'Error occured', 'null')
            

    

class EditProfileApi(webapp.RequestHandler):
    def post(self):
        self.handler()

    def handler(self):
        request = self.request
        response = self.response
        logging.info('[EditProfileApi]')
        try:
            user = gforum.users.getAuthorizedUser(self.request, self.response)
            if not user:
                gforum.util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to edit profile', 'null')
                return
            nick_name    = gforum.util.normText(request.get('nick_name'))
            if nick_name:
                gforum.users.editUserProfile(user, 'nick_name',nick_name)
            first_name   = gforum.util.normText(request.get('first_name'))
            if first_name:
                gforum.users.editUserProfile(user, 'first_name',first_name)
            last_name    = gforum.util.normText(request.get('last_name'))
            if last_name:
                gforum.users.editUserProfile(user, 'last_name',last_name)
            where_from = gforum.util.normText(request.get('where_from'))
            if where_from:
                gforum.users.editUserProfile(user, 'where_from',where_from)
            email = gforum.util.normText(request.get('email'))
            logging.info('email=%s' % email)
            #rex = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
            if email:
                logging.info('if email:')
                gforum.users.editUserProfile(user, 'email',email)
                #if len(rex.findall(email))>==0:
                #    raise ValueError('Wrong value for email')
            gravatar_email = gforum.util.normText(request.get('gravatar_email'))
            logging.info('gravatar_email=%s' % gravatar_email)
            gravatar_size = gforum.util.normText(request.get('gravatar_size'))
            logging.info('gravatar_size=%s' % gravatar_size)
            if gravatar_email and gravatar_size:
                gforum.users.saveUserGravatar(user, gravatar_email, gravatar_size)
            # 
            # save data to users profile here! 
            # 
            gforum.util.writeApiResponse(response, 'ok', 'ok', 'null')
        except ValueError, va:
            msg = str(va)
            logging.info('Error when edit profile: %s' % msg)
            gforum.util.writeApiResponse(response, 'fail', msg, 'null')    
        except:
            logging.error('Error occured')
            gforum.util.writeApiResponse(response, 'fail', 'Error occured', 'null')    

application = webapp.WSGIApplication([
  #(format('%s/api/v1/post_message'   % gforum_root), PostMessageApi),
  #(format('%s/api/v1/create_thread'  % gforum_root), CreateThreadApi),
  #(format('%s/api/v1/create_forum'   % gforum_root), CreateForumApi),
  #(format('%s/api/v1/edit_profile'   % gforum_root), EditProfileApi)
  ('%s/api/v1/post_message'   % gforum_root, PostMessageApi),
  ('%s/api/v1/create_thread'  % gforum_root, CreateThreadApi),
  ('%s/api/v1/create_forum'   % gforum_root, CreateForumApi),
  ('%s/api/v1/edit_profile'   % gforum_root, EditProfileApi)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
