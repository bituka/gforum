#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import gforum.settings
import gforum.users
import gforum.util

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
gforum_theme = gforum.settings.GFORUM_THEME

class GForumProfilePage(webapp.RequestHandler):

    def get(self):
        key_str = self.request.url[self.request.url.rfind('/')+1:]
        key = db.Key(key_str)
        profile_user    = gforum.users.getUser(key)
        tpl = gforum.util.getDefaultTemplateData(self.request, self.response, gforum_root)     
        authorized_user = tpl['user']
        is_other_user = True
        if authorized_user and profile_user.key() == authorized_user.key():
            is_other_user = False

        tpl['is_other_user'] = is_other_user
        tpl['profile_user'] = profile_user
        
        template_path = 'themes/%s/profile.html' % gforum_theme
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, tpl).decode('utf-8'))


application = webapp.WSGIApplication([
  ('%s/profile/.*' % gforum_root,  GForumProfilePage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
