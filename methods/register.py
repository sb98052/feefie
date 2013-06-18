from lib.method import Method
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.api.users import *
import json
from google.appengine.api import channel
from lib.exception import *
from db.user import *
import time

class register(Method):
    role = None

    def call(self, user, req, response):
        email = req.get('email')
        tname,taddr = utils.parseaddr(email)
        parts = taddr.split('@')
        uid = parts[0]
        user = User.get_user(uid)

        if (not user):
            user = User.create_user(uid.lower(),email)

        response.out.write('Your key is: %s'%user.hash)





