from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.ext import db
from datetime import datetime
from datetime import *
from hashlib import md5
from email import utils
import copy
import random
import logging
import os
import base64
from google.appengine.api.channel import *

def safe_md5(s):
    return md5(s.encode('utf-8')).hexdigest()

class AuthError(Exception):
       def __init__(self, value):
           self.parameter = value

       def __str__(self):
           return repr(self.parameter)

class User(db.Expando):
    user = db.UserProperty()
    uid = db.StringProperty()
    baseid = db.StringProperty()
    hash = db.StringProperty()
    email = db.StringProperty()
    effective_email = db.StringProperty()
    passwd = db.StringProperty()
    source_email = db.StringProperty()

    @classmethod
    def get_user_auth(cls,uid,p):
        u = cls.gql('WHERE uid=:1 and passwd=:2',uid,p).get()
        if (not u):
            raise AuthError('User %s not found or incorrect passwd: %s'%(uid,p))

        return u
              
        
    @classmethod
    def create_user(cls,uid,email):
        key = '__exists_%s'%uid
        memcache.delete(key)
        u = cls()
        u.uid = uid
        u.email = email
        u.passwd = base64.urlsafe_b64encode(os.urandom(12))
        u.put()

    @classmethod 
    def get_user(cls,uname):
        key = '__exists_%s'%uname
        ukey = memcache.get(key)
        if (ukey is None):
            user = cls.gql('WHERE uid=:1',uname).get()
            try:
                memcache.set(key,str(user.key()))
            except AttributeError:
                logging.info('User %s not found'%uname)
        else:
            user = db.get(db.Key(encoded=ukey))

        if (user):
            uhash = safe_md5(user.uid+user.passwd)
            user.hash = uhash
            ret = user
        else:
            ret = None

        return ret


