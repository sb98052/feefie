import logging, email
from handle_mail import *

import webapp2
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        handle_mail(mail_message)

application = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
