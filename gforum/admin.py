#!/usr/bin/env python
#

import sys
import os
import logging
import wsgiref.handlers

from gforum.forum import getAllForums

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

gforum_root  = '/forum'
gforum_theme = 'default'

class GForumAdminPage(webapp.RequestHandler):

    @login_required
    def get(self):
        if users.is_current_user_admin():
            forums = getAllForums()

            has_forums = len(forums)>0
            
            template_values = {
                'logout_url' : users.create_logout_url(gforum_root),
                'forumpath'  : gforum_root,
                'has_forums' : has_forums,
                'forums'     : forums
            }
            template_path = 'themes/%s/admin/main.html' % gforum_theme
            path = os.path.join(os.path.dirname(__file__), template_path)
            self.response.out.write(template.render(path, template_values).decode('utf-8'))

        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write('<html><body>This page is only for administrators</body></html>')


application = webapp.WSGIApplication([
  #(format('%s/admin.*' % gforum_root),  GForumAdminPage)
  ('%s/admin.*' % gforum_root,  GForumAdminPage),
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
