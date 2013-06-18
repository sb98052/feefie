from db.cheapchannel import CheapChannel
from google.appengine.api.channel import *
from db.event import *
import time

class DispatchPage(webapp.RequestHandler):
  def process_http(self):
    channel_id = self.request.get('from')
    e = Event.gql('WHERE channel_ids=:1',channel_id)
    e.channel_ids.remove(channel_id)
    e.put()
    return;
    
  def get(self):
    self.process_http()
    
  def post(self):
    self.process_http()
    

application = webapp.WSGIApplication(
                                     [(r'/.*', DispatchPage)],
                                     debug=False)
