#!/usr/bin/env python

import cgi
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

AUTH_PROVIDER_GOOGLE   = 1
AUTH_PROVIDER_FACEBOOK = 2
AUTH_PROVIDER_TWITTER  = 3
AUTH_PROVIDER_VKONTAKTE= 4
AUTH_PROVIDER_YANDEX   = 5
AUTH_PROVIDER_MAILRU   = 6
AUTH_PROVIDER_OPENID   = 7

class GForumVkontakteData(db.Model):
    loginza_response = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity = db.StringProperty()
    provider = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    nick_name = db.StringProperty()
    gender    = db.StringProperty()
    dob       = db.StringProperty()
    country   = db.StringProperty()
    photo     = db.BlobProperty()
    photo_ct  = db.StringProperty()
    uid       = db.StringProperty()

class GForumGoogleData(db.Model):
    loginza_response = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity = db.StringProperty()
    provider = db.StringProperty()
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    full_name = db.StringProperty()
    email = db.StringProperty()
    language = db.StringProperty()
    country  = db.StringProperty()
    uid = db.StringProperty()

class GForumTwitterData(db.Model):
    loginza_response = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity = db.StringProperty()
    provider = db.StringProperty()
    photo     = db.BlobProperty()
    photo_ct  = db.StringProperty()
    biography = db.StringProperty()
    web_default = db.StringProperty()
    nick_name = db.StringProperty()
    full_name = db.StringProperty()
    uid = db.StringProperty()

class GForumGravatarData(db.Model):
    size = db.IntegerProperty()
    email= db.StringProperty()
    hash = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    
class GForumUser(db.Model):
    first_name = db.StringProperty()
    last_name  = db.StringProperty()
    nick_name  = db.StringProperty()
    nick_name_lower = db.StringProperty()
    email        = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    last_login_date = db.DateTimeProperty()
    use_gravatar = db.BooleanProperty()
    avatar       = db.BlobProperty()
    avatar_ct    = db.StringProperty()
    gravatar     = db.ReferenceProperty(GForumGravatarData)
    avatar_url   = db.StringProperty()
    where_from   = db.StringProperty()
    messages_number = db.IntegerProperty()
    signature = db.StringProperty()
    auth_provider = db.StringProperty()
    auth_provider_identity = db.StringProperty()
    vkontakte_data   = db.ReferenceProperty(GForumVkontakteData)
    google_data      = db.ReferenceProperty(GForumGoogleData)
    twitter_data     = db.ReferenceProperty(GForumTwitterData)
    
class GForumOptions(db.Model):
    allow_guest_posts = db.BooleanProperty()
    
class GForumStatistics(db.Model):
    threads_number   = db.IntegerProperty()
    messages_number = db.IntegerProperty()
    last_post_date  = db.DateTimeProperty()

class GForumMessage(db.Model):
    text = db.TextProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(GForumUser)
    thread_key = db.StringProperty()
    
class GForum(db.Model):
    name        = db.StringProperty()
    permalink   = db.StringProperty()
    description = db.StringProperty(multiline=True)
    create_date = db.DateTimeProperty(auto_now_add=True)
    last_post_date = db.DateTimeProperty()
    options     = db.ReferenceProperty(GForumOptions)
    statistics  = db.ReferenceProperty(GForumStatistics)
    messages_number  = db.IntegerProperty()
    last_message     = db.ReferenceProperty(GForumMessage)
    threads_number   = db.IntegerProperty()
    thread_list      = db.ListProperty(db.Key)

class GForumThread(db.Model):
    title = db.StringProperty()
    permalink = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    messages_number = db.IntegerProperty()
    views_number    = db.IntegerProperty()
    message_list    = db.ListProperty(db.Key)
    thread_starter  = db.ReferenceProperty(GForumUser)
    forum = db.ReferenceProperty(GForum)
    last_message = db.ReferenceProperty(GForumMessage)
    
class GForumSession(db.Model):
    session_key = db.StringProperty()
    gforum_user = db.ReferenceProperty(GForumUser)
    ip_address   = db.StringProperty()
    expire_date  = db.DateTimeProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date  = db.DateTimeProperty(auto_now=True)

class GForumImage(db.Model):
    blob = db.BlobProperty()
    content_type = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date  = db.DateTimeProperty(auto_now=True)
    is_avatar    = db.BooleanProperty()

