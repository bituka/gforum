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
import datetime
from hashlib import md5

from gforum import models
from gforum import settings

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))


def getSessionExpireTime():
    return datetime.datetime.now() + datetime.timedelta(minutes=settings.GFORUM_SESSION_EXPIRE_INTERVAL)
    
def createSessionObject(remote_address):
    session = models.GForumSession()
    session.session_key = md5('%s%s%s' % (datetime.datetime.now(), settings.GFORUM_SESSION_SECRET_KEY, remote_address)).hexdigest()
    session.expire_date = getSessionExpireTime()
    session.ip_address = remote_address
    session.put()
    return session

#
# see http://code.google.com/p/gae-sessions/
# http://gaeutilities.appspot.com/session
# see http://popcnt.org/2008/05/google-app-engine-tips.html
#
def getOrCreateCurrentSession(request, response):
    logging.info('[getOrCreateCurrentSession] begin')
    sess_key = None
    try:
        sess_key = request.cookies[settings.GFORUM_SESSION_COOKIE_NAME]
        logging.info('[getOrCreateCurrentSession] cookie set! cookie=\'%s\'' % sess_key)
    except KeyError:
        logging.info('[getOrCreateCurrentSession] no cookie set')
        pass
    if sess_key:
        valid_sessions = models.GForumSession.all().filter('session_key =', sess_key).filter('expire_date >', datetime.datetime.now()).fetch(limit=1)
        if len(valid_sessions)>0:
            session = valid_sessions[0]
            session.expire_date = getSessionExpireTime()
            session.put()
            logging.info('[getOrCreateCurrentSession] returning existing session')
            return session
    # create session
    session = createSessionObject(request.remote_addr)
    # this doesn't work for setting cookie
    #response.set_cookie(SESSION_COOKIE_KEY, session.session_key)
    # instead use Set-Cookie header
    logging.info('[getOrCreateCurrentSession] setting cookie')
    response.headers.add_header('Set-Cookie','%s=%s; path=/' % (settings.GFORUM_SESSION_COOKIE_NAME, session.session_key))
    return session

def getSession(sess_key):
    valid_sessions = models.GForumSession.all().filter('session_key =', sess_key).filter('expire_date >', datetime.datetime.now()).fetch(limit=1)
    if len(valid_sessions)>0:
        session = valid_sessions[0]
        session.expire_date = getSessionExpireTime()
        session.put()
        logging.info('[getSession] returning existing session')
        return session
    else:
        logging.info('[getSession] found no valid sessions')
        return None

def getAuthorizedUser(request, response):
    try:
        sess_key = request.cookies[settings.GFORUM_SESSION_COOKIE_NAME]
        logging.info('[getAuthorizedUser] sess_key=%s' % sess_key)
        session = getSession(sess_key)
        if session:
            return session.gforum_user
        else:
            return None
    except KeyError:
        logging.info('[getAuthorizedUser] no cookie detected')
        return None
    

def putUserIntoCurrentSession(user, request, response):
    session = getOrCreateCurrentSession(request, response)
    session.gforum_user = user
    session.put()

def finishSession(request, response):
    logging.info('[finishSession] begin')
    session = getOrCreateCurrentSession(request, response)
    session.delete()
    # this doesn't work to delete cookie
    # response.delete_cookie(gforum.settings.GFORUM_SESSION_COOKIE_NAME)
    logging.info('[finishSession] setting cookie')
    response.headers.add_header('Set-Cookie','%s=%s; path=/; expires=Fri, 31-Dec-2001 23:59:59 GMT; ' % (settings.GFORUM_SESSION_COOKIE_NAME, 'session_deleted'))

