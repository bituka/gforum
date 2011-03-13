#!/usr/bin/env python
#

#import TestModule

from gforum.forum  import createNewForum
from gforum.forum  import getForum
from gforum.thread import createNewEmptyThread
import sys
import os
import logging
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class TestPage(webapp.RequestHandler):

    def get(self):
        test = self.request.url[self.request.url.rfind('test'):]
        self.response.out.write('<h1>%s</h1>' % test)
        if test == 'test1':
            for i in range(5):
                createNewForum('myforum %d' % (i+1), None, None, None)
            self.response.out.write('Created 5 forums')
        elif test == 'test2':
            forum_url = 'myforum_1'
            f = getForum(forum_url)
            if not f:
                raise ValueError('Cannot retrieve forum with url "%s"' % forum_url)
            for i in range(5):
                createNewEmptyThread(f, 'thread %d' % (i+10))
            self.response.out.write('Created 5 new empty threads')
        #for i in range(5):
        #    createNewForum('myforum %d' % (i+1), None, None, None)
        
    
application = webapp.WSGIApplication([
  ('/test.*', TestPage)
], debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
