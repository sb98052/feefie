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

class subscribe(Method):
    role = None

    def call(self, user, req, response):
        h = req.get('hash')
        e = Event.gql('WHERE hash=:1',h).get()
        html = req.get('html')
        if (not e):
            response.out.write('Not found')
        else:
            c = greedy_create_channel(e)
            if (html=='1'):
                str="""
                <html>
                <head>
                    <script type="text/javascript" src="/_ah/channel/jsapi"></script>
                </head>
                <body>
                <script>
                    var eCount=0;
                    function onMessage(m) { 
                        eCount=eCount+1;
                    }

                    function onError(error) {
                        alert('Reconnect to you need.');
                    }

                    function onClose() 
                    {
                    }

                    function onOpen() 
                    {
                    }

                    channel = new goog.appengine.Channel('%s');
                    socket = channel.open();
                    socket.onmessage = onMessage;
                    socket.onerror = onError;
                    socket.onclose = onClose;
                    socket.onopen = onOpen;
                </script>
                <p>Please wait</p>
                </body>
                </html>
                """%c
                response.out.write(str)
            else:
                response.out.write(json.dumps({'status':0,'token':c}))

