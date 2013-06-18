import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users

import json

import datetime
import copy
import urllib
import random
import logging
from sets import Set
import os
from hashlib import md5
from lib.exception import *
import methods

from method_list import supported_actions

class DispatchPage(webapp2.RequestHandler):
  def process_http(self):
    try:
        action = self.request.get('action')
        action_name = action
        if (action not in supported_actions):
            logging.info('Weird action %s invoked not in %s'%(action_name,str(supported_actions)))
            if (action_name):
                raise BareError('The action you invoked is not supported. Please go back in your browser and try again.')
            else:
                return

        if ('Development' in os.environ['SERVER_SOFTWARE']):
            method_module = __import__(".".join(['methods',action]),fromlist=['methods'])
        else:
            try:
                method_module = __import__(".".join(['methods',action]),fromlist=['methods'])
            except ImportError,e:
                logging.error('Error importing module: %s'%str(e))
                raise BareError('Whoops, it appears that your URL is malformed. Please go back in your browser and try again.')

        method = getattr(method_module, action)
        user = users.get_current_user()

        action = method(self)
        
        if (method.role and not user):
            file = self.request.path
            lfile = 'login.html'

            path = os.path.join(os.path.dirname(__file__), 'html/%s'%lfile)
            language = self.request.get('language')

            if (language):
                lang = language
            else:
                lang='en'


            file = self.request.path
            path = os.path.join(os.path.dirname(__file__), 'html/%s'%lfile)
            di = {'continue':urllib.quote(self.request.uri),'loopback':urllib.quote(self.request.uri.split('?')[0]),'error':self.request.get('error')}
            self.response.out.write(template.render(path, di))
        else:
            action.webob = self
            self.response.headers["Access-Control-Allow-Origin"]="*"
            action.root_path = os.path.dirname(__file__)
            if (user):
                e = user.email()
            else:
                e = 'Not logged in'
            action.html_context = {}
            action(user, self.request, self.response)

    except BareError, e:
        self.response.out.write(str(e))

  def get(self):
    self.process_http()
    
    
  def post(self):
    self.process_http()
    

application = webapp2.WSGIApplication(
                                     [(r'/command', DispatchPage)],
                                     debug=False)
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
