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

from gforum import models
from gforum import util
from gforum import settings
from gforum import sessions
from gforum import dao

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH
gforum_theme = settings.GFORUM_THEME

###############################################################################
#################################### HANDLERS #################################
###############################################################################

class GForumAbstractHandler(webapp.RequestHandler):
    def getDefaultTemplateData(self):
        logging.info('[GForumAbstractHandler.getDefaultTemplateData]')
        user = sessions.getAuthorizedUser(self.request, self.response)
        
        user_authorized = True if user else False
        if not user_authorized:
            logging.info('User is not authorized, viewing forums as guest')
        else:
            logging.info('Detected authorized user')
        
        template_values = {
            'user_authorized' : user_authorized,
            'user'            : user,
            'forumpath'       : gforum_root,
            'host'            : '%s://%s' % (self.request.scheme, self.request.host)
        }
        return template_values
        
    def getTemplatePath(self, name):
        template_path = 'themes/%s/%s' % (gforum_theme, name)
        path = os.path.join(os.path.dirname(__file__), template_path)
        return path
        
    def renderTemplate(self, name, tpl):
        path = self.getTemplatePath(name)
        self.response.out.write(template.render(path, tpl).decode('utf-8'))

    def redirectForumHome(self):
        logging.info('[GForumAbstractHandler.redirectForumHome]')
        self.redirect(gforum_root)
        
    def redirect500(self):
        logging.info('[GForumAbstractHandler.redirect500]')
        self.redirect('%s/500.html' % gforum_root)
        
    def redirect404(self):
        logging.info('[GForumAbstractHandler.redirect404]')
        self.redirect('%s/404.html' % gforum_root)
    
class GForum403Handler(webapp.RequestHandler):
    def get(self):
        pass
        
class GForum404Handler(GForumAbstractHandler):
    def get(self):
        self.renderTemplate('404.html', {})

class GForum500Handler(GForumAbstractHandler):
    def get(self):
        self.renderTemplate('500.html', {})

class GForumMainHandler(GForumAbstractHandler):
    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            self.redirect500()

    def handle(self):
        logging.info('[GForumMainHandler.handle]')
        forums = dao.getAllForums()
        has_forums = len(forums)>0

        template_values = self.getDefaultTemplateData()
        template_values['has_forums'] = has_forums
        template_values['forums']     = forums

        self.renderTemplate('main.html', template_values)
        

class GForumForumHandler(GForumAbstractHandler):
    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            self.redirect500()
            
    def handle(self):
        logging.info('[GForumForumHandler.handle]')
        permalink = self.extractForumPermalink()
        forum = dao.getForumByPermalink(permalink)
        if not forum:
            self.redirect404()
            return

        has_threads = len(forum.thread_list)>0
        threads = []
        
        if len(forum.thread_list)>0:
            threads = dao.getAllForumThreads(forum)

        template_values = self.getDefaultTemplateData()
        template_values['has_threads'] = has_threads
        template_values['forum']    = forum
        template_values['threads']  = threads

        self.renderTemplate('forum.html', template_values)
        
    def extractForumPermalink(self):
        lookup_string = '%s/f/' % gforum_root
        permalink = self.request.url[self.request.url.find(lookup_string)+len(lookup_string):]
        logging.info('[extractForumPermalink] permalink=\'%s\'' % permalink)
        return permalink

class GForumThreadHandler(GForumAbstractHandler):
    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            self.redirect500()
        
    def handle(self):
        logging.info('[GForumThreadHandler.handle]')
        thread_id = self.extractThreadId()
        data = dao.getThreadAndMessages(thread_id)
        thread   = data['thread']
        messages = data['messages']

        template_values = self.getDefaultTemplateData()
        template_values['thread']   = thread
        template_values['forum']    = thread.forum
        template_values['messages'] = messages
        
        self.renderTemplate('thread.html', template_values)
        dao.incrementThreadViews(thread)     
        
    def extractThreadId(self):
        lookup_string = '%s/t/' % gforum_root
        idx1 = self.request.url.find(lookup_string)+len(lookup_string)
        idx2 = self.request.url.find('/',idx1)
        thread_id = self.request.url[idx1:idx2]
        logging.info('[extractThreadId] thread_id=\'%s\'' % thread_id)
        return thread_id           

class GForumImageHandler(webapp.RequestHandler):
    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            pass
            
    def handle(self):
        key_str = self.request.url[self.request.url.rfind('/')+1:]
        key = db.Key(key_str)
        image = models.GForumImage.get(key)
        if image:
            self.response.headers['Content-Type'] = image.content_type
            self.response.out.write(image.blob)
        else:
            pass

class GForumProfileHandler(GForumAbstractHandler):
    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            self.redirect500()

    def handle(self):
        user_key_str = self.request.url[self.request.url.rfind('/')+1:]
        profile_user    = dao.getUser(user_key_str)
        if not profile_user:
            self.redirect404()
        else:
            template_values = self.getDefaultTemplateData()
            authorized_user = template_values['user']
            is_other_user = True
            if authorized_user and profile_user.key() == authorized_user.key():
                is_other_user = False
        
            template_values['is_other_user'] = is_other_user
            template_values['profile_user']  = profile_user
            self.renderTemplate('profile.html', template_values)
        
class GForumSitemapHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumLoginzaLoginHandler(GForumAbstractHandler):
    def get(self):
        self.redirectForumHome()

    def post(self):
        try: 
            loginza_token = self.request.get('token')
            logging.info('[GForumLoginzaLoginHandler.post] loginza_token = \'%s\'' % loginza_token)
            loginza_url = 'http://loginza.ru/api/authinfo?token=%s' % loginza_token
            result = util.fetchUrl(loginza_url)
            if result.status_code == 200:
                logging.info('[GForumLoginzaLoginHandler.post] result.content=\'%s\'' % result.content)
                self.handleLoginzaResponse(result.content)
            else:
                logging.error('[GForumLoginzaLoginHandler.post] cannot fetch data from loginza!')
                self.redirectForumHome()
        except:
            logging.error('[GForumLoginzaLoginHandler.post] Error occured: cannot fetch data from loginza!')
            if settings.GFORUM_USE_VKONTAKTE_EMULATOR:
                logging.error('[GForumLoginzaLoginHandler.post] Running loginza emulator...')
                content = '%s%s%s%s' % ('{"identity":"http:\/\/vkontakte.ru\/id27610","provider":"http:\/\/vkontakte.ru\/","uid":27610,', 
                  '"name":{"first_name":"\u0418\u0432\u0430\u043d","last_name":"\u0420\u044b\u043d\u0434\u0438\u043d"},', 
                  '"nickname":"","gender":"M","dob":"1983-03-18","address":{"home":{"country":"1"}},',
                  '"photo":"http:\/\/cs408.vkontakte.ru\/u27610\/e_8e8b9f02.jpg"}')
                self.handleLoginzaResponse(content)
        self.redirectForumHome()

    def handleLoginzaResponse(self, content):
        logging.info('[GForumLoginzaLoginHandler.handleLoginzaResponse]')
        try: 
            obj = util.loadJson(content)
            provider = obj['provider']
            identity = obj['identity']
            logging.info('[GForumLoginzaLoginHandler.handleLoginzaResponse] provider = \'%s\'' % provider)
            logging.info('[GForumLoginzaLoginHandler.handleLoginzaResponse] identity = \'%s\'' % identity)
            user = dao.searchUser(identity)
            if user:
                logging.info('[GForumLoginzaLoginHandler.handleLoginzaResponse] User already registered on the forum! User identity: \'%s\'' % user.auth_provider_identity)
            else:
                logging.info('[GForumLoginzaLoginHandler.handleLoginzaResponse] New user comes. Register user on the forum! User identity: \'%s\'' % identity)
                user = dao.createNewUser(obj, content)
            # put user into session here...
            sessions.putUserIntoCurrentSession(user, self.request, self.response)
        except Exception, e:
            logging.error('Exception: "%s"' % e)
            logging.error('Error occured when handling JSON from Loginza')
            logging.error('content=\'%s\'' % content)
        self.redirectForumHome()


class GForumLoginzaLogoutHandler(GForumAbstractHandler):
    def get(self):
        sessions.finishSession(self.request, self.response)
        self.redirectForumHome()
     
