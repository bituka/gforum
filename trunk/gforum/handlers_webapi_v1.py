#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2011 Ivan Ryndin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

__author__ = 'Ivan P. Ryndin'

import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

from gforum import settings
from gforum import sessions
from gforum import util
from gforum import dao

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH
gforum_theme = settings.GFORUM_THEME

###############################################################################
#################################### HANDLERS #################################
###############################################################################

class GForumCreateForumApiHandler(webapp.RequestHandler):
    def post(self):
        try:
            if not users.is_current_user_admin():
                util.writeApiResponse(self.response, 'fail', 'you are not admin', '')
            else:
                self.handle()
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except:
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')

    def handle(self):
        logging.info('[GForumCreateForumApiHandler.handle]')

        forum_id          = self.request.get('forum_id')
        forum_name        = self.request.get('forum_name')
        forum_permalink   = self.request.get('forum_permalink').lower()
        forum_description = self.request.get('forum_description')
        logging.info('[[GForumCreateForumApiHandler.handle]] forum_name=%s' % forum_name)
        logging.info('[[GForumCreateForumApiHandler.handle]] forum_permalink=%s' % forum_permalink)
        logging.info('[[GForumCreateForumApiHandler.handle]] forum_description=%s' % forum_description)
        if forum_id and len(forum_id.strip())>0:
            forum = dao.updateForum(forum_id, forum_name, forum_permalink, forum_description)
        else: 
            forum = dao.createNewForum(forum_name, forum_permalink, forum_description)
        rendered_forum = dao.renderForumJson(forum)
        util.writeApiResponse(self.response, 'ok', 'ok', rendered_forum)

class GForumListForumsApiHandler(webapp.RequestHandler):
    def get(self):
        try:
            if not users.is_current_user_admin():
                util.writeApiResponse(self.response, 'fail', 'you are not admin', '')
            else:
                self.handle()
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except:
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')

    def handle(self):
        logging.info('[GForumListForumsApiHandler.handle]')
        
        forums = dao.getAllForums()
        rendered_forums = dao.renderForumJson(forums)
        util.writeApiResponse(self.response, 'ok', 'ok', rendered_forums)
        
class GForumCreateThreadApiHandler(webapp.RequestHandler):
    def post(self):
        try:
            user = sessions.getAuthorizedUser(self.request, self.response)
            if user:
                self.handle(user)
            else:
                util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to create threads', 'null')
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except Exception, e:
            logging.error('[GForumCreateThreadApiHandler.post] error: %s' % e)
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')                

    def handle(self, user):
        logging.info('[GForumCreateThreadApiHandler.handle]')
        forum_key    = self.request.get('forum_key')
        thread_title = self.request.get('thread_title')
        message_text = self.request.get('message_text')
        logging.info('[GForumCreateThreadApiHandler.handle] forum_key=\'%s\'' % forum_key)
        logging.info('[GForumCreateThreadApiHandler.handle] thread_title=\'%s\'' % thread_title)
        logging.info('[GForumCreateThreadApiHandler.handle] message_text=\'%s\'' % message_text)
        thread = dao.createNewThread(forum_key, thread_title, message_text, user)
        util.writeApiResponse(self.response, 'ok', 'ok', 'null')
          
class GForumPostMessageApiHandler(webapp.RequestHandler):
    def post(self):
        try:
            user = sessions.getAuthorizedUser(self.request, self.response)
            if user:
                self.handle(user)
            else:
                util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to post messages', 'null')
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except Exception, e:
            logging.error('[GForumPostMessageApiHandler.post] error: %s' % e)
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')                

    def handle(self, user):
        logging.info('[GForumPostMessageApiHandler.handle]')
        thread_key   = self.request.get('thread_key')
        message_text = self.request.get('message_text')
        logging.info('[GForumPostMessageApiHandler.handle] thread_key=\'%s\''   % thread_key)
        logging.info('[GForumPostMessageApiHandler.handle] message_text=\'%s\'' % message_text)
        thread = dao.createNewMessage(thread_key, message_text, user)
        util.writeApiResponse(self.response, 'ok', 'ok', 'null')      
        
class GForumCheckNicknameApiHandler(webapp.RequestHandler):  
    def post(self):
        self.handler()
    

    def get(self):
        self.handler()
     
    def handler(self):   
        try:
            self.doHandle()
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except:
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')

    def doHandle(self):
        request = self.request
        response = self.response
        logging.info('[GForumCheckNicknameApiHandler]')
        try:
            nickname = request.get('nickname')
            result = dao.isNicknameUsed(nickname)
            util.writeApiResponse(response, 'ok', 'ok', '{"isNicknameUsed" : %s}' % ('true' if result else 'false'))
        except ValueError, ve:
            msg = 'Wrong value! ' + str(ve)
            logging.info('[GForumCheckNicknameApiHandler] error: ' + msg)
            util.writeApiResponse(response, 'fail', msg, '')
        except Exception, ex:
            logging.info('[GForumCheckNicknameApiHandler] error!! ' + str(ex))
            util.writeApiResponse(response, 'fail', 'Error occured', 'null')            
     
     
class GForumCheckEmailApiHandler(webapp.RequestHandler):  
    def post(self):
        self.handler()
    

    def get(self):
        self.handler()
     
    def handler(self):   
        try:
            self.doHandle()
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except:
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')

    def doHandle(self):
        request = self.request
        response = self.response
        logging.info('[GForumCheckEmailApiHandler]')
        try:
            email = request.get('email')
            result = dao.isEmailUsed(email)
            util.writeApiResponse(response, 'ok', 'ok', '{"isEmailUsed" : %s}' % ('true' if result else 'false'))
        except ValueError, ve:
            msg = 'Wrong value! ' + str(ve)
            logging.info('[GForumCheckEmailApiHandler] error: ' + msg)
            util.writeApiResponse(response, 'fail', msg, '')
        except Exception, ex:
            logging.info('[GForumCheckEmailApiHandler] error!! ' + str(ex))
            util.writeApiResponse(response, 'fail', 'Error occured', 'null')       
            
class GForumEditProfileApiHandler(webapp.RequestHandler):
    def post(self):
        try:
            user = sessions.getAuthorizedUser(self.request, self.response)
            if user:
                self.handle(user)
            else:
                util.writeApiResponse(response, 'fail', 'Only authorized users are allowed to edit profiles', 'null')
        except ValueError, e:
            util.writeApiResponse(self.response, 'fail', str(e), 'null')
        except Exception, e:
            logging.error('[GForumEditProfileApiHandler.post] error: %s' % e)
            util.writeApiResponse(self.response, 'fail', 'Error occured', 'null')                

    def handle(self, user):
        logging.info('[GForumEditProfileApiHandler.handle]')
        nick_name    = self.request.get('nick_name').strip()
        email        = self.request.get('email').strip()
        first_name   = self.request.get('first_name').strip()
        last_name    = self.request.get('last_name').strip()
        where_from   = self.request.get('where_from').strip()
        #logging.info('nick_name = %s' % nick_name)
        #logging.info('email = %s' % email)
        #logging.info('first_name = %s' % first_name)
        #logging.info('last_name = %s' % last_name)
        #logging.info('where_from = %s' % where_from)
        
        data = {
            'nick_name': nick_name,
            'email': email,
            'first_name':first_name,
            'last_name':last_name,
            'where_from':where_from
        }
        thread = dao.editUserProfile(user, data)
        util.writeApiResponse(self.response, 'ok', 'ok', 'null')              
