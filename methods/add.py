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

def add_event(user, n):
    uid = user.uid
    event = Event()
    event.title = n['title']
    event.created = int(time.time())
    event.modified = event.created
    event.hash = n['hash']
    try:
        event.parent_hash = n['parent_hash']
    except KeyError:
        pass

    try:
        # Optional fields
        event.attributes = int(n['attributes'])
        event.efire = n['efire']
        event.enotify = n['enotify']
    except KeyError:
        pass

    if (event.parent_hash==''):
        event.parent_hash=None

    event.put()

class add(Method):
    role = None

    def call(self, user, req, response):
        uid = req.get('u')
        try:
            user = User.get_user(uid)
            espec = req.get('event')
            event = json.loads(espec)

            existing = Event.gql('WHERE title=:1 and user=:2',event['title'],uid).get()
            if (existing):
                res = {'status':0,'hash':existing.hash,'new':False}
            else:
                event['hash'] = safe_md5(uid+event['title'])
                add_event(user, event)
                res = {'status':0,'hash':event['hash'],'new':False}
        except AuthError,e:
            logging.info(str(e))
            res = {'status':-2,'error':str(e)}

        response.out.write(json.dumps(res))
