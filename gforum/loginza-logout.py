#!/usr/bin/env python
#

import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import gforum.users
import gforum.settings

gforum_root  = gforum.settings.GFORUM_FORUM_PATH
view_root    = '%s/view' % gforum_root

class GForumLogoutLoginzaPage(webapp.RequestHandler):

    def get(self):
        gforum.users.finishSession(self.request, self.response)
        self.redirect(view_root)


application = webapp.WSGIApplication([
  ('%s/logout/loginza' % gforum_root,  GForumLogoutLoginzaPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
