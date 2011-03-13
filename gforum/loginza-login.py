#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from google.appengine.api import urlfetch

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson as json

import gforum.users
import gforum.settings

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
view_root    = '%s/view' % gforum_root
USE_VKONTAKTE_EMULATOR = True

class GForumLoginLoginzaPage(webapp.RequestHandler):
    def get(self):
        self.redirect(view_root)

    def post(self):
        try: 
            loginza_token = self.request.get('token')
            logging.info('loginza_token = \'%s\'' % loginza_token)
            url = 'http://loginza.ru/api/authinfo?token=%s' % loginza_token
            result = urlfetch.fetch(url)
            if result.status_code == 200:
                #obj = json.loads( string )
                logging.info('result.content=\'%s\'' % result.content)
                self.handleLoginzaResponse(result.content)
            else:
                logging.error('cannot fetch data from loginza!')
        except:
            logging.error('Error occured: cannot fetch data from loginza!')
            if USE_VKONTAKTE_EMULATOR:
                logging.error('Running loginza emulator...')
                content = '%s%s%s%s' % ('{"identity":"http:\/\/vkontakte.ru\/id27610","provider":"http:\/\/vkontakte.ru\/","uid":27610,', 
                  '"name":{"first_name":"\u0418\u0432\u0430\u043d","last_name":"\u0420\u044b\u043d\u0434\u0438\u043d"},', 
                  '"nickname":"","gender":"M","dob":"1983-03-18","address":{"home":{"country":"1"}},',
                  '"photo":"http:\/\/cs408.vkontakte.ru\/u27610\/e_8e8b9f02.jpg"}')
                self.handleLoginzaResponse(content)
        self.redirect(view_root)

    def handleLoginzaResponse(self, response):
        logging.info('[handleLoginzaResponse]')
        try: 
            obj = json.loads(response)
            provider = obj['provider']
            identity = obj['identity']
            logging.info('provider = \'%s\'' % provider)
            logging.info('identity = \'%s\'' % identity)
            user = gforum.users.searchUser(identity)
            if user:
                logging.info('User already registered on the forum! User identity: \'%s\'' % user.auth_provider_identity)
            else:
                logging.info('New user comes. Register user on the forum! User identity: \'%s\'' % identity)
                user = gforum.users.createNewUser(obj, response)
            # put user into session here...
            gforum.users.putUserIntoCurrentSession(user, self.request, self.response)
        except Exception, inst:
            logging.error('Exception: "%s"' % inst)
            logging.error('Error occured when handling JSON from Loginza')
            logging.error('response=\'%s\'' % response)
        self.redirect(view_root)


        
    
        
application = webapp.WSGIApplication([
  ('%s/login/loginza' % gforum_root,  GForumLoginLoginzaPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
