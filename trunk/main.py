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

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

gforum_root  = settings.GFORUM_FORUM_PATH

class GForumMainRedirectPage(webapp.RequestHandler):
    def get(self):
        self.redirectGForumHome()
        
    def redirectGForumHome(self):
        self.redirect(gforum_root)

        
AROUTES = [
    ('/', GForumMainRedirectPage),
]

def main():
    application = webapp.WSGIApplication(AROUTES, debug=False)
    run_wsgi_app(application)
    
if __name__ == '__main__':
  main()
