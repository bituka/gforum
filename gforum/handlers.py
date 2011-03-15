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
from gforum import settings

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH
gforum_theme = settings.GFORUM_THEME

###############################################################################
#################################### HANDLERS #################################
###############################################################################

class GForumAbstractHandler(webapp.RequestHandler):
    def getDefaultTemplateData(self):
        logging.info('[GForumAbstractHandlerþgetDefaultTemplateData]')
        user = gforum.users.getAuthorizedUser(self.request, self.response)
        
        user_authorized = True if user else False
        logging.info('user=%s' % user)
        user.avatar_url = gforum.users.getAvatarUrl(user, gforum_root)
        
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
    
class GForum403Handler(webapp.RequestHandler):
    def get(self):
        pass
        
class GForum404Handler(webapp.RequestHandler):
    def get(self):
        pass

class GForumMainHandler(GForumAbstractHandler):

    def get(self):
        try: 
            self.handle()
        except Exception, e:
            logging.error('%s: \'%s\'' % (self.__class__.__name__, str(e)))
            pass

    def handle(self):
        forums = models.GForumForum.all().order('name').fetch()
        has_forums = len(forums)>0

        template_values = self.getDefaultTemplateData()
        template_values['has_forums'] = has_forums
        template_values['forums']     = forums

        path = self.getTemplatePath('main.html')
        self.response.out.write(template.render(path, template_values).decode('utf-8'))
        

class GForumForumHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumThreadHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumAvatarHandler(webapp.RequestHandler):
    def get(self):
        pass

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

class GForumProfileHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumSitemapHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumLoginzaLoginHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumLoginzaLogoutHandler(webapp.RequestHandler):
    def get(self):
        pass

class GForumApiv1Handler(webapp.RequestHandler):
    def get(self):
        pass

class GForumAdminHandler(webapp.RequestHandler):
    def get(self):
        pass

        
