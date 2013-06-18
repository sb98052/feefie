from lib.method import Method
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.api.users import *
import json
from google.appengine.api import channel
from lib.exception import *
from db.user import *
from db.event import *
import time

def fire(user, n):
    uid = user.uid
    event = Event.gql('WHERE hash=:1 and eto=:2',n['hash'],uid).get()

    if (event):
        event.fire()

def fires(user, eventstr):
    uid = user.uid
    events = json.loads(eventstr)
    to_delete = []
    for n in events:
        deferred.defer(fire, user, n)
        fire(user, n)

    db.delete(to_delete)

class fire(Method):
    role = None

    def call(self, user, req, response):
        h = req.get('hash')
        p = req.get('payload')
        e = Event.gql('WHERE hash=:1',h).get()
        if (not e):
            response.out.write(json.dumps({'status':-1,'error':'Event not found'}))
        else:
            for c in e.channel_ids:
                channel.send_message(c,p)

