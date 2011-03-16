#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import re
import os
import sys
import logging
import datetime
from hashlib import md5

from gforum.models import GForumGravatarData
from gforum.models import GForumSession
from gforum.models import GForumUser
from gforum.models import GForumGoogleData
from gforum.models import GForumVkontakteData
from gforum.models import GForumTwitterData

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import gforum.settings
import gforum.util

gforum_root  = gforum.settings.GFORUM_FORUM_PATH

def incrementMessageNumber(user):
    if not user.messages_number:
        user.messages_number = 0
    user.messages_number = user.messages_number + 1
    user.put()
    
def getUser(key):
    user = GForumUser.get(key)
    return user

def getAvatar(key):
    user = GForumUser.get(key)
    if user and user.avatar and user.avatar_ct:
        data = {
            'avatar': user.avatar,
            'content_type': user.avatar_ct
        }
        return data
    else:
        return None

def searchUser(identity):
    logging.info('[users.searchUser], identity=\'%s\'' % identity)
    list = GForumUser.all().filter('auth_provider_identity =',identity).fetch(limit=1)
    if len(list)>0:
        return list[0]
    else:
        return None
        

def editUserProfile(user, field, value):
    logging.info('[users.editUserProfile]')
    if field == 'nick_name':
        normValue = gforum.util.normText(value)
        if normValue:
            lowerValue = normValue.strip().lower()
            users = GForumUser.all().filter('nick_name_lower =', lowerValue).fetch(limit=1)
            if len(users)>0:
                if users[0].key() == user.key():
                    return
                raise ValueError('User with this nickname is already registered')
            user.nick_name       = normValue
            user.nick_name_lower = lowerValue
        else:
            raise ValueError('Wrong value for nickname')
        user.nick_name = value
    elif field == 'first_name':
        user.first_name = value
    elif field == 'last_name':
        user.last_name = value
    elif field == 'where_from':
        user.where_from = value
    elif field == 'email':
        if not gforum.util.validateEmail(value):
            raise ValueError('Wrong value for email')
        user.email = value
    logging.info('before user.put()')
    user.put()

def saveUserGravatar(user, gravatar_email, gravatar_size):
    logging.info('[users.saveUserGravatar]')
    if not gforum.util.validateEmail(gravatar_email):
        raise ValueError('Wrong value for email')
    gravatar = user.gravatar
    if not gravatar:
        gravatar = GForumGravatarData()
    gravatar.email = gravatar_email.lower().strip()
    gravatar.hash  = md5(gravatar.email).hexdigest()
    # gravatar size should be integer and should not exceed 100 px
    try: 
        gravatar.size  = int(gravatar_size)
    except:
        gravatar.size = 100
    if gravatar.size > 100:
        gravatar.size = 100
    gravatar.put()
    user.gravatar = gravatar
    user.use_gravatar = True
    user.avatar_url = 'http://gravatar.com/avatar/%s?s=%s' % (user.gravatar.hash, user.gravatar.size)
    user.put()
    
def getAvatarUrl(user, gforum_root):
    result = '%s/avatar/%s' % (gforum_root, user.key())
    if user.use_gravatar:
        if user.gravatar:
            result = 'http://gravatar.com/avatar/%s?s=%s' % (user.gravatar.hash, user.gravatar.size)
        else:
            # use fake hash and mystery man
            result = 'http://gravatar.com/avatar/a420cdcb62f1915612f5ca91696e211e?s=50&d=mm'
    return result 
    
def createNewUser(obj, objStr):
    provider = obj['provider'] 
    
    user = GForumUser()
    user.auth_provider = provider
    user.auth_provider_identity = obj['identity']
    user.messages_number = 0

    if provider.find('vkontakte.ru')>-1:
        data = createNewVKontakteData(obj, objStr)
        user.vkontakte_data = data 
        user.first_name     = data.first_name
        user.last_name      = data.last_name
        user.avatar         = data.photo
        user.avatar_ct      = data.photo_ct
        user.nick_name      = data.nick_name.strip()
        if len(user.nick_name)==0:
            user.nick_name = '%s %s' % (user.first_name, user.last_name)
    elif provider.find('google.com')>-1:
        data = createNewGoogleData(obj, objStr)
        user.google_data = data
        user.first_name  = data.first_name
        user.last_name   = data.last_name
        user.nick_name   = data.full_name
        user.email       = data.email
    elif provider.find('twitter.com')>-1:
        data = createNewTwitterData(obj, objStr)
        user.twitter_data = data
        user.nick_name   = data.nick_name
        user.avatar      = data.photo
        user.avatar_ct   = data.photo_ct
    user.nick_name_lower = user.nick_name.strip().lower()
    user.put()
    user.avatar_url = '%s/avatar/%s' % (gforum_root, user.key())
    user.put()
    return user
    

def createNewVKontakteData(obj, objStr):
    data = GForumVkontakteData()
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
    url = obj['photo']
    # fetch photo data from VKontakte
    try:
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            data.photo = result.content
        data.photo_ct = gforum.util.getImageContentTypeByUrl(url)
    except:
        logging.error('Cannot fetch user photo by URL: \'%s\'' % url)
    data.put()
    
    return data

def createNewGoogleData(obj, objStr):
    data = GForumGoogleData()
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
    data = GForumTwitterData()
    data.loginza_response = objStr
    data.identity  = obj['identity']
    data.provider  = obj['provider']
    data.biography = obj['biography']
    data.web_default = obj['wev']['default']
    data.nick_name = obj['nickname']
    data.full_name = obj['name']['full_name']
    data.uid       = str(obj['uid'])
    url = obj['photo']
    # fetch photo data from VKontakte
    try:
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            data.photo = result.content
        data.photo_ct = gforum.util.getImageContentTypeByUrl(url)
    except:
        logging.error('Cannot fetch user photo by URL: \'%s\'' % url)
    data.put()
    return data
