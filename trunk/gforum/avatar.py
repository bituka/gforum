#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from gforum.users import getAvatar

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

import gforum.settings

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
gforum_theme = gforum.settings.GFORUM_THEME

class GForumAvatarPage(webapp.RequestHandler):

    def get(self):
        logging.info('[GForumAvatarPage]')
        key_str = self.request.url[self.request.url.rfind('/')+1:]
        key = db.Key(key_str)
        data = getAvatar(key)
        if data:
            self.response.headers['Content-Type'] = data['content_type']
            self.response.out.write(data['avatar'])
        else:
            # output empty icon here
            pass

application = webapp.WSGIApplication([
  ('%s/avatar/.*' % gforum_root,  GForumAvatarPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
