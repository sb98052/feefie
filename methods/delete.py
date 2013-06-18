from lib.method import Method
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.api.users import *
import json
from google.appengine.api import channel
from lib.exception import *
from db.user import *
from db.note import *
import time

def delete_note(user, n):
    uid = user.uid
    note = Note.gql('WHERE hash=:1 and eto=:2',n['hash'],uid).get()

    if (note):
        note.deleted=True
        note.modified = int(time.time())
        note.put()
        user.wake_up()

def update_note(user, n):
    uid = user.uid
    try:
        note = Note.gql('WHERE hash=:1 and eto=:2',n['hash'],uid).get()
    except KeyError,e:
        logging.info('Note does not have a hash:')
        logging.info(n)
        logging.info(e)
        return

    if (note):
        note.title = n['title']
        note.modified = int(time.time())
        note.content = n['content']
        note.attributes = int(n['attributes'])
        try:
            note.update_id = int(n['index']) # This should be < 0. Client will check this value in case of multiple concurrent updates
        except TypeError:
            pass

        logging.info('Set note %s attribute to %d'%(note.title,note.attributes))
        note.put()
        user.wake_up()
    else:
        logging.info('Note not found')

def add_note(user, n):
    uid = user.uid
    note = Note()
    note.title = n['title']
    note.created = int(time.time())
    note.modified = note.created
    note.content = str(n['content'])
    note.attributes = int(n['attributes'])
    note.hash = n['hash']
    note.parent_hash = n['parent_hash']
    if (note.parent_hash==''):
        note.parent_hash=None
    note.eto = uid
    note.put()
    user.wake_up()

def add_notes(user, notestr):
    uid = user.uid
    notes = json.loads(notestr)
    logging.info(str( notes))
    for n in notes:
        deferred.defer(add_note, user, n)

def update_notes(user, notestr):
    uid = user.uid
    notes = json.loads(notestr)
    logging.info('Notes to be updated:')
    logging.info(str( notes))
    for n in notes:
        deferred.defer(update_note, user, n)

def delete_notes(user, notestr):
    uid = user.uid
    notes = json.loads(notestr)
    to_delete = []
    for n in notes:
        deferred.defer(delete_note, user, n)
        delete_note(user, n)

    db.delete(to_delete)

class p(Method):
    role = None

    def call(self, user, req, response):
        uid = req.get('u')
        try:
            user = User.get_user(uid)
            add_events(user, req.get('new_notes'))
            update_notes(user, req.get('updated_notes'))
            delete_notes(user, req.get('deleted_notes'))
            res = {'status':0}
        except AuthError,e:
            logging.info(str(e))
            res = {'status':-2,'error':str(e)}

        response.out.write(json.dumps(res))
