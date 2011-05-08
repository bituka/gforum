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
import hashlib

from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from gforum import models
from gforum import util
from gforum import settings

# Log a message each time this module get loaded.
logging.info('Loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))

def getUser(user_key_str):
    key = db.Key(user_key_str)
    return models.GForumUser.get(key)
    
def renderJsonTemplate(name, tpl):
    path = os.path.join(os.path.dirname(__file__), 'json/%s' % name)
    robj = template.render(path, tpl)
    return robj
    
def getForumByPermalink(permalink):
    forums = models.GForumForum.all().filter('permalink =',permalink.lower()).fetch(limit=1)
    if len(forums)>0:
        return forums[0]
    else:
        return None

def getAllForums():
    forums = models.GForumForum.all().order('name').fetch(limit=1000)
    return forums    
    
def createNewForum(name, permalink, description):
    logging.info('[createNewForum]')
    name = util.normTextValue(name)
    if not name:
        raise ValueError('forum_name')

    permalink = util.normTextValue(permalink)
    if not permalink:
        permalink = name
    permalink = util.makeCorrectPermalink(permalink)
    description = util.normHtmlValue(description)
    forum = getForumByPermalink(permalink)
    if forum:
        raise ValueError('forum_exist')
    forum = models.GForumForum()
    forum.name = name
    forum.permalink = permalink
    forum.description = description
    forum.thread_list = []
    forum.messages_number = 0
    forum.threads_number = 0
    forum.put()
    return forum

def updateForum(id, name, permalink, description):
    logging.info('[updateForum]')
    id = int(id)
    forum = models.GForumForum.get_by_id(id)
    if not forum:
        raise ValueError('forum_id')
        
    name = util.normTextValue(name)
    if not name:
        raise ValueError('forum_name')

    permalink = util.normTextValue(permalink)
    if not permalink:
        permalink = name
    permalink = util.makeCorrectPermalink(permalink)
    description = util.normHtmlValue(description)
    forum2 = getForumByPermalink(permalink)
    if forum2 and forum2.key().id() != id:
        raise ValueError('forum_exist')

    forum.name = name
    forum.permalink = permalink
    forum.description = description
    forum.put()
    return forum
    
def renderForumJson(f):
    if type(f) == type([]):
        tpl = {
            'forums': f
        }
        return renderJsonTemplate('forums.json', tpl)
    else:
        tpl = {
            'forum': f
        }
        return renderJsonTemplate('forum.json', tpl)

def getAllForumThreads(forum):
    threads = models.GForumThread.get(forum.thread_list)
    return threads
    
def searchUser(user_identity):
    logging.info('[dao.searchUser], user_identity=\'%s\'' % user_identity)
    list = models.GForumUser.all().filter('auth_provider_identity =',user_identity).fetch(limit=1)
    if len(list)>0:
        return list[0]
    else:
        return None
        
def createNewUser(obj, objStr):
    provider = obj['provider'] 
    
    user = models.GForumUser()
    user.auth_provider_identity = obj['identity']
    user.messages_number = 0
    user.message_list = []
    
    avatar_url = None
    
    if provider.find('vkontakte.ru')>-1:
        user.auth_provider = 'vkontakte'
        data = createNewVkontakteData(obj, objStr)
        user.auth_provider_key = str(data.key())
        user.first_name     = data.first_name
        user.last_name      = data.last_name
        avatar_url          = data.avatar_url
        user.nick_name      = data.nick_name.strip()
        if len(user.nick_name)==0:
            user.nick_name = '%s %s' % (user.first_name, user.last_name)
    elif provider.find('google.com')>-1:
        user.auth_provider = 'google'
        data = createNewGoogleData(obj, objStr)
        user.auth_provider_key = str(data.key())
        user.first_name  = data.first_name
        user.last_name   = data.last_name
        user.nick_name   = data.full_name
        user.email       = data.email
    elif provider.find('twitter.com')>-1:
        user.auth_provider = 'twitter'
        data = createNewTwitterData(obj, objStr)
        user.auth_provider_key = str(data.key())        
        user.nick_name   = data.nick_name
        avatar_url       = data.avatar_url
    elif provider.find('facebook.com')>-1:
        user.auth_provider = 'facebook'
        data = createNewFacebookData(obj, objStr)
        user.auth_provider_key = str(data.key())
        user.first_name  = data.first_name
        user.last_name   = data.last_name
        user.nick_name   = data.full_name.strip()
        avatar_url       = data.avatar_url
        user.email       = data.email     
    elif provider.find('myopenid.com')>-1:
        user.auth_provider = 'myopenid'
        data = createNewMyopenidData(obj, objStr)
        user.auth_provider_key = str(data.key())
        user.nick_name   = data.nick_name
    
    user.use_gravatar = False
    
    image = None
    if avatar_url:
        image = fetchAndSaveAvatar(avatar_url)
        if image:
            user.image_key = str(image.key())
            
    if not avatar_url and user.email:
        m = hashlib.md5()
        m.update(user.email)
        user.gravatar_hash = m.hexdigest()
        user.use_gravatar = True

    user.nick_name_lower = user.nick_name.strip().lower()
    user.put()
    
    if image:
        image.author_key = str(user.key())
        image.put()
    return user

def createNewMyopenidData(obj, objStr):
    data = models.GForumMyopenidData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.full_name = obj['name']['full_name']
    data.nick_name = obj['nickname']
    data.gender    = obj['gender']
    data.language  = obj['language']
    data.dob       = obj['dob']
    data.country   = obj['address']['home']['country']
    data.put()
    return data
    
def createNewFacebookData(obj, objStr):
    data = models.GForumFacebookData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.uid       = str(obj['uid'])    
    data.first_name= obj['name']['first_name']
    data.last_name = obj['name']['last_name']
    data.full_name = obj['name']['full_name']    
    data.gender    = obj['gender']
    data.dob       = obj['dob']
    data.email     = obj['email']
    data.avatar_url= obj['photo']
    data.put()
    return data
    
def createNewVkontakteData(obj, objStr):
    data = models.GForumVkontakteData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.first_name= obj['name']['first_name']
    data.last_name = obj['name']['last_name']
    data.nick_name = obj['nickname']
    data.gender    = obj['gender']
    data.dob       = obj['dob']
    data.uid       = str(obj['uid'])
    data.country   = obj['address']['home']['country']
    data.avatar_url= obj['photo']
    data.put()
    return data

def createNewGoogleData(obj, objStr):
    data = models.GForumGoogleData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.first_name= obj['name']['first_name']
    data.last_name = obj['name']['last_name']
    data.full_name = obj['name']['full_name']
    data.email     = obj['email']
    data.language  = obj['language']
    data.uid       = str(obj['uid'])
    data.country   = obj['address']['home']['country']
    data.put()
    return data

def createNewTwitterData(obj, objStr):
    data = models.GForumTwitterData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.biography = obj['biography']
    data.web_default = obj['web']['default']
    data.nick_name = obj['nickname']
    data.full_name = obj['name']['full_name']
    data.uid       = str(obj['uid'])
    data.avatar_url= obj['photo']
    data.put()
    return data
        
def fetchAndSaveAvatar(url):
    try:
        result = util.fetchUrl(url)
        if result.status_code == 200:
            image = models.GForumImage()
            image.blob = result.content
            # get image width, height
            # resize avatar if necessary
            image_object = images.Image(image.blob)
            if image_object.width > settings.GFORUM_MAX_AVATAR_SIZE or image_object.height > settings.GFORUM_MAX_AVATAR_SIZE:
                image_object.resize(settings.GFORUM_MAX_AVATAR_SIZE,settings.GFORUM_MAX_AVATAR_SIZE)
            image.width  = image_object.width
            image.height = image_object.height
            image.content_type = util.getImageContentTypeByUrl(url)
            image.is_avatar = True
            image.put()
            return image
        else:
            return None
    except:
        logging.error('[dao.fetchAndSaveAvatar] cannot fetch image from url: \'%s\'' % url)
        return None

def createNewThread(forum_key_str, thread_title, message_text, user):
    # check user
    if not user:
        raise ValueError('user')

    # check message
    message_text = checkMessageText(message_text)

    # check forum
    forum_key = db.Key(forum_key_str)
    forum = models.GForumForum.get(forum_key)
    if not forum:
        raise ValueError('forum')
        
    # save all data
    thread = createNewEmptyThread(forum, thread_title, user)
    message = createNewMessageUnchecked(thread, user, message_text)
    addThreadMessage(thread, message)
    addThreadAndMessageToForum(forum, thread, message)
    addUserMessage(user, message)
    return thread   

def checkMessageText(msg_txt):
    msg_txt = util.normHtmlValue(msg_txt)
    if not msg_txt:
        raise ValueError('message')
    return msg_txt

def checkThreadTitle(title):
    title = util.normTextValue(title)
    if not title:
        raise ValueError('thread')
    return title
    
def createNewEmptyThread(forum, title, user):
    title = checkThreadTitle(title)
    thread = models.GForumThread()
    thread.title = title
    thread.permalink   = util.makeCorrectPermalink(title)
    thread.messages_number = 0
    thread.views_number    = 1
    thread.message_list    = []
    thread.thread_starter  = user
    thread.forum = forum
    thread.put()
    return thread
    
def createNewMessageUnchecked(thread, user, message_text):
    message = models.GForumMessage()
    message.text = message_text
    message.user = user
    message.thread_key = str(thread.key())
    message.put()        
    return message
    
def addThreadMessage(thread, msg):
    thread.message_list.append(msg.key())
    thread.messages_number = thread.messages_number + 1
    thread.last_message = msg
    thread.put()    
    
def addThreadAndMessageToForum(forum, thread, message):
    forum.thread_list.append(thread.key());
    forum.threads_number  = forum.threads_number+1
    forum.messages_number = forum.messages_number+1
    forum.last_message = message
    forum.put()
    
def addMessageToForum(forum, message):
    forum.messages_number = forum.messages_number+1
    forum.last_message = message
    forum.put()
        
def addUserMessage(user, message):
    user.message_list.append(message.key())
    user.messages_number = len(user.message_list)
    user.put()
    
def createNewMessage(thread_key_str, message_text, user):
    # check user
    if not user:
        raise ValueError('user')

    # check message
    message_text = checkMessageText(message_text)

    # check thread
    thread_key = db.Key(thread_key_str)
    thread = models.GForumThread.get(thread_key)
    if not thread:
        raise ValueError('thread')
        
    forum = thread.forum
    
    # save all data
    message = createNewMessageUnchecked(thread, user, message_text)
    addThreadMessage(thread, message)
    addMessageToForum(forum, message)
    addUserMessage(user, message)
    return message
    
def incrementThreadViews(thread):
    logging.info('[dao.incrementThreadViews]')
    if not thread.views_number:
        thread.views_number = 0
    thread.views_number = thread.views_number + 1
    thread.put()
    
def getThreadAndMessages(thread_id):
    thread_id = int(thread_id)
    thread = models.GForumThread.get_by_id(thread_id)
    if not thread:
        raise ValueError('thread_id')
    messages = models.GForumMessage.get(thread.message_list)
    result = {
        'thread'   : thread,
        'messages' : messages
    }
    return result

def isNicknameUsed(nickname):
    nickname2 = nickname.strip().lower()
    users = models.GForumUser.all().filter('nick_name_lower',nickname2).fetch(limit=1)
    if len(users)>0:
        return True
    else:
        return False
    
def isEmailUsed(email):
    email2 = email.strip().lower()
    users = models.GForumUser.all().filter('email',email2).fetch(limit=1)
    if len(users)>0:
        return True
    else:
        return False
        
def editUserProfile(user, data):
    nick_name = data['nick_name'].strip()
    email     = data['email'].strip()
    if len(nick_name) == 0:
        raise ValueError('Nickname shouldn\'t be empty')
    if not util.validateEmail(email):
        raise ValueError('Invalid email address')
    if user.email != data['email'] and isEmailUsed(data['email']):
        raise ValueError('This email is already in use')
    if user.nick_name != data['nick_name'] and isNicknameUsed(data['nick_name']):
        raise ValueError('This nickname is already in use')
    
    first_name = data['first_name'].strip()
    if len(first_name)==0:
        first_name = None
    last_name = data['last_name'].strip()
    if len(last_name)==0:
        last_name = None
    where_from = data['where_from'].strip()
    if len(where_from)==0:
        where_from = None
    
    user.nick_name = nick_name
    user.nick_name_lower = nick_name.strip().lower()
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.where_from = where_from
    
    user.put()
    
    
    
    
