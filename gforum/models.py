#!/usr/bin/env python
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

from google.appengine.ext import db

class GForumMyopenidData(db.Model):
    loginza_response = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity    = db.StringProperty()
    provider    = db.StringProperty()
    full_name   = db.StringProperty()
    nick_name   = db.StringProperty()
    language    = db.StringProperty()
    country     = db.StringProperty()
    gender      = db.StringProperty()
    dob         = db.StringProperty()

class GForumFacebookData(db.Model):
    loginza_response = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity  = db.StringProperty()
    provider  = db.StringProperty()
    uid       = db.StringProperty()
    first_name= db.StringProperty()
    last_name = db.StringProperty()
    full_name = db.StringProperty()
    gender    = db.StringProperty()
    dob       = db.StringProperty()
    email     = db.StringProperty()
    avatar_url= db.StringProperty()

class GForumVkontakteData(db.Model):
    loginza_response = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity  = db.StringProperty()
    provider  = db.StringProperty()
    first_name= db.StringProperty()
    last_name = db.StringProperty()
    nick_name = db.StringProperty()
    gender    = db.StringProperty()
    dob       = db.StringProperty()
    country   = db.StringProperty()
    avatar_url= db.StringProperty()
    uid       = db.StringProperty()

class GForumGoogleData(db.Model):
    loginza_response = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity    = db.StringProperty()
    provider    = db.StringProperty()
    first_name  = db.StringProperty()
    last_name   = db.StringProperty()
    full_name   = db.StringProperty()
    email       = db.StringProperty()
    language    = db.StringProperty()
    country     = db.StringProperty()
    uid         = db.StringProperty()

class GForumTwitterData(db.Model):
    loginza_response = db.StringProperty()
    create_date  = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    identity = db.StringProperty()
    provider = db.StringProperty()
    avatar_url= db.StringProperty()
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
    avatar_url   = db.StringProperty()
    where_from   = db.StringProperty()
    messages_number = db.IntegerProperty()
    message_list    = db.ListProperty(db.Key)
    signature = db.StringProperty()
    auth_provider = db.StringProperty()
    auth_provider_identity = db.StringProperty()
    auth_provider_key = db.StringProperty()
    
class GForumMessage(db.Model):
    text = db.TextProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(GForumUser)
    thread_key = db.StringProperty()
    
class GForumForum(db.Model):
    name        = db.StringProperty()
    permalink   = db.StringProperty()
    description = db.StringProperty(multiline=True)
    create_date = db.DateTimeProperty(auto_now_add=True)
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
    forum = db.ReferenceProperty(GForumForum)
    last_message = db.ReferenceProperty(GForumMessage)
    
class GForumSession(db.Model):
    session_key  = db.StringProperty()
    gforum_user  = db.ReferenceProperty(GForumUser)
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

