import logging
import traceback
import json

class BareError(Exception):
     def __init__(self, value):
         logging.error('User received error message: %s for trace:'%value)
         for s in traceback.format_stack():
             logging.error(s.rstrip())
         self.value = value

     def __str__(self):
         return str(self.value)
