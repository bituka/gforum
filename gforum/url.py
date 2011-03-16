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
from google.appengine.ext.webapp.util import run_wsgi_app

from gforum import settings
from gforum import handlers
from gforum import handlers_admin
from gforum import handlers_webapi_v1
from gforum import timings

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH

ROUTES = [
    ('%s/403.html'      % gforum_root, handlers.GForum403Handler),
    ('%s/404.html'      % gforum_root, handlers.GForum404Handler),
    ('%s/500.html'      % gforum_root, handlers.GForum500Handler),
    ('%s'               % gforum_root, handlers.GForumMainHandler),
    ('%s/'              % gforum_root, handlers.GForumMainHandler),
    ('%s/f/.*'          % gforum_root, handlers.GForumForumHandler),
    ('%s/t/.*'          % gforum_root, handlers.GForumThreadHandler),
    ('%s/avatar/.*'     % gforum_root, handlers.GForumAvatarHandler),
    ('%s/image/.*'      % gforum_root, handlers.GForumImageHandler),
    ('%s/profile/.*'    % gforum_root, handlers.GForumProfileHandler),
    ('%s/sitemap.xml'   % gforum_root, handlers.GForumSitemapHandler),
    ('%s/login/loginza' % gforum_root, handlers.GForumLoginzaLoginHandler),
    ('%s/logout/loginza'% gforum_root, handlers.GForumLoginzaLogoutHandler),
    ('%s/api/v1/create_forum'  % gforum_root, handlers_webapi_v1.GForumCreateForumApiHandler),
    ('%s/api/v1/create_thread' % gforum_root, handlers_webapi_v1.GForumCreateThreadApiHandler),
    ('%s/admin.*'       % gforum_root, handlers_admin.GForumAdminHandler)
]

def main():
    path = timings.start_run()
    application = webapp.WSGIApplication(ROUTES, debug=settings.GFORUM_DEBUG)
    run_wsgi_app(application)
    timings.stop_run(path)
    
if __name__ == '__main__':
  main()
