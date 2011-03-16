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
from google.appengine.ext.webapp.util import login_required


from gforum import models
from gforum import settings
from gforum import sessions

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH
gforum_theme = settings.GFORUM_THEME

###############################################################################
#################################### HANDLERS #################################
###############################################################################

class GForumAdminAbstractHandler(webapp.RequestHandler):
    def getDefaultTemplateData(self):
        logging.info('[GForumAdminAbstractHandler.getDefaultTemplateData]')
        
        template_values = {
            'forumpath'       : gforum_root,
            'host'            : '%s://%s' % (self.request.scheme, self.request.host),
            'logout_url'      : users.create_logout_url(gforum_root)
        }
        return template_values
        
    def getTemplatePath(self, name):
        template_path = 'themes/%s/admin/%s' % (gforum_theme, name)
        path = os.path.join(os.path.dirname(__file__), template_path)
        return path
    
class GForumAdminHandler(GForumAdminAbstractHandler):
    @login_required
    def get(self):
        try: 
            if users.is_current_user_admin():
                self.handle()
            else:
                self.response.headers['Content-Type'] = 'text/html'
                self.response.out.write('<html><body>This page is only for administrators</body></html>')
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            self.redirect500()

    def handle(self):
        forums = models.GForumForum.all().order('name').fetch(limit=1000)
        has_forums = len(forums)>0
        
        template_values = self.getDefaultTemplateData()
        template_values['has_forums'] = has_forums
        template_values['forums'] = forums

        path = self.getTemplatePath('main.html')
        self.response.out.write(template.render(path, template_values).decode('utf-8'))

        
