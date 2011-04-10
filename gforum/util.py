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

import random          
import os
import re
import sys
import logging
import datetime
from hashlib import md5

from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

from django.utils import simplejson

import gforum.settings

def writeApiResponse(response,status,errorMsg,data):
    logging.info('[UtilModule.writeResponse]')
    response.set_status(200)
    response.headers['Content-Type'] = 'application/json'
    if not data:
        data = '""'
    response_tpl_val = {
        'status'   : status,
        'errorMsg' : errorMsg,
        'data'     : data
    }
    responseTplPath = os.path.join(os.path.dirname(__file__), 'json/api.json')
    resp = template.render(responseTplPath, response_tpl_val)
    response.out.write(resp)

def escapeString(s):
    if s and len(s)>0:
        result = re.sub('''(['"])''', r'\\\1', s)
        result = result.strip()
        arr = result.splitlines();
        r = ''
        for a in arr:
            r = r+a+' '
        return r
    return s

def translit(theString):
    assert theString is not str, "Error: argument MUST be string"

    try:
        s = unicode(theString,"utf-8")    
    except TypeError, te:
        s = theString
        
    table1 = {
        u' ':'_',
        u'а':'a',
        u'б':'b',
        u'в':'v',
        u'г':'g',
        u'д':'d',
        u'е':'e',
        u'ё':'jo',
        u'ж':'zh',
        u'з':'z',
        u'и':'i',
        u'й':'jj',
        u'к':'k',
        u'л':'l',
        u'м':'m',
        u'н':'n',
        u'о':'o',
        u'п':'p',
        u'р':'r',
        u'с':'s',
        u'т':'t',
        u'у':'u',
        u'ф':'f',
        u'х':'kh',
        u'ц':'c',
        u'ч':'ch',
        u'ш':'sh',
        u'щ':'shh',
        u'ъ':'',
        u'ы':'y',
        u'ь':'',
        u'э':'eh',
        u'ю':'ju',
        u'я':'ja',
        u'А':'A',
        u'Б':'B',
        u'В':'V',
        u'Г':'G',
        u'Д':'D',
        u'Е':'E',
        u'Ё':'Jo',
        u'Ж':'Zh',
        u'З':'Z',
        u'И':'I',
        u'Й':'Jj',
        u'К':'K',
        u'Л':'L',
        u'М':'M',
        u'Н':'N',
        u'О':'O',
        u'П':'P',
        u'Р':'R',
        u'С':'S',
        u'Т':'T',
        u'У':'U',
        u'Ф':'F',
        u'Х':'Kh',
        u'Ц':'C',
        u'Ч':'Ch',
        u'Ш':'Sh',
        u'Щ':'Shh',
        u'Ъ':'',
        u'Ы':'Y',
        u'Ь':'',
        u'Э':'Eh',
        u'Ю':'Ju',
        u'Я':'Ja'    
    }

    result = []
    for c in s:
        tc = table1.get(c)
        if not tc and tc != '':
            tc = c
        result.append(tc)
    return ''.join(result)

def htc(m):
    return chr(int(m.group(1),16))

# see http://stackoverflow.com/questions/1276764/stripping-everything-but-alphanumeric-chars-from-a-string-in-python
def makeCorrectPermalink(txt):
    txt = translit(txt)
    return re.sub('[\W]+', '', txt).lower()
    
# taken from there: http://jaytaylor.com/blog/2010/04/25/urldecode-for-python-one-liner/
def urldecode(url):
    rex = re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M)
    return rex.sub(htc,url)
 
passwordSymbols = ";*()_+=-,.[]{}1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
 
def genRandomSymbols(len):
    """
    :param len: length of random symbols sequence
    :raise BadValueError: If len < 0
    :return: The random sequence of len length.
    """
    if len < 0:
        raise ValueError("len should be greater or equal than 0")
    elif len == 0:
        return ""
    else:
        result = ""
        for i in range(len):
            result = result + random.choice(passwordSymbols)
        return result

def normTextValue(v):
    if not v:
        v = ''
    v = v.strip()
    if len(v)==0:
        return None
    else:
        return v

def normHtmlValue(v):
    v = normTextValue(v)    
    if v:
        v = v.replace('\n','<br/>').replace('\'', '&quot;').replace('"', '&quot;')
    return v

def getImageContentTypeByUrl(url):
    url = url.lower()
    ct = None
    if url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.jpe'):
        ct = 'image/jpeg'
    elif url.endswith('.png'):
        ct = 'image/png'
    elif url.endswith('.gif'):
        ct = 'image/gif'
    elif url.endswith('.svg'):
        ct = 'image/svg+xml'
    return ct

def validateEmail(email):
    rex = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
    if len(rex.findall(email))==0:
        return False
    else:
        return True
        
def fetchUrl(url):
    return urlfetch.fetch(url)
    
def loadJson(strJson):
    return simplejson.loads(strJson)    

def generateImageUrl(image):
    return 
