from google.appengine.api import users,datastore_errors
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.channel import *
import base64
import logging
import sys
import os

class Event(db.Expando):
  attributes = db.IntegerProperty(default=0)
  title = db.StringProperty(multiline=True)
  ctitle = db.StringProperty(multiline=True)
  created = db.IntegerProperty()
  modified = db.IntegerProperty()
  enotify = db.StringProperty()
  efire = db.StringProperty()
  hash = db.StringProperty()
  user = db.StringProperty()
  parent_hash = db.StringProperty()
  depth = db.IntegerProperty(default=2)
  is_parent = db.BooleanProperty()
  channel_ids = db.StringListProperty()

  def wake_up(self,msg='.'):
    for clid in self.channel_ids:
        send_message(str(clid),msg)
        logging.info('Messaging %s (%s)'%(clid,msg))


def add_channel_to_event(channel,event):
    if (channel.clid not in user.channel_ids):
        user.channel_ids.append(channel.clid)

    user.put()

def remove_channel_from_event(channel,event):
    if (channel.clid in user.channel_ids):
        user.channel_ids.remove(channel.clid)

# Greedy refers to the fact that we're creating a new channel
# per connection, whereas it is possible to reuse channels.
def greedy_create_channel(event):
    clid = base64.urlsafe_b64encode(os.urandom(12))
    try:
        token = create_channel(clid)
    except InvalidChannelClientIdError:
        logging.info('Invalid channel: %s'%clid)
        return

    event.channel_ids.append(clid)
    event.put()
    return token
