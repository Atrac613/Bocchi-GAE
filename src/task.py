# -*- coding: utf-8 -*-

import os
import logging
import urllib
import urllib2
import datetime
import random

from base64 import b64encode

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from django.utils import simplejson
from pytz import timezone
import pytz

from db import BotPrefs
from db import BotMessage
from db import UserPrefs
from db import DevicePrefs

from conf.settings import UA_APPLICATION_KEY
from conf.settings import UA_APPLICATION_MASTER_SECRET

class FindDeviceTask(webapp.RequestHandler):
    def post(self):
        user_id = self.request.get('user_id')
        bot_id = self.request.get('bot_id')
        
        bot_prefs = BotPrefs.get_by_id(int(bot_id))
        if bot_prefs is None:
            logging.error('bot_id is invalid.')
            return
        
        user_prefs = UserPrefs.get_by_id(int(user_id))
        if user_prefs is None:
            logging.error('user_id is invalid.')
            return
        
        if user_prefs.free_quantity <= 0 and user_prefs.paid_quantity <= 0:
            logging.error('quantity is invalid.')
            return
        
        device_list = DevicePrefs.all().filter('google_account =', user_prefs.google_account).fetch(10)
        for device in device_list:
            logging.info('Add notify task.')
            try:
                bot_id = user_prefs.bot_prefs_key.key().id()
                taskqueue.add(url = '/task/send_notify', params = {'user_id': user_prefs.key().id(), 'device_token': device.device_token, 'bot_id': bot_id})
            except:
                logging.error('Add task failed.')
        

class SendNotifyTask(webapp.RequestHandler):
    def post(self):
        device_token = self.request.get('device_token')
        user_id = self.request.get('user_id')
        bot_id = self.request.get('bot_id')
        logging.info('SendNotifyTask')
        
        bot_prefs = BotPrefs.get_by_id(int(bot_id))
        if bot_prefs is None:
            logging.error('bot_id is invalid.')
            return
        
        user_prefs = UserPrefs.get_by_id(int(user_id))
        if user_prefs is None:
            logging.error('user_id is invalid.')
            return
        
        if user_prefs.free_quantity <= 0 and user_prefs.paid_quantity <= 0:
            logging.error('quantity is invalid.')
            return
        
        date = datetime.datetime.now(tz=timezone(user_prefs.timezone))
        logging.info('Date: %s' % date)
        hour = date.hour
        logging.info('Hour: %d' % hour)
        
        time = '%02d00-%02d00' % (hour, hour+1)
        
        logging.info('time: %s' % time)
        
        bot_message_list = BotMessage.all().filter('bot_prefs_key =', bot_prefs.key()).filter('time =', time).fetch(10)
        
        message_list = []
        
        for bot_message in bot_message_list:
            message_list.append(bot_message.message)
            
        if len(message_list) > 0:
            rand = random.randint(0, len(message_list)-1)
            message = message_list[rand]
        else:
            logging.error('message is empty.')
            return
        
        logging.info('message: %s' % message)
        
        url = 'https://go.urbanairship.com/api/push/'
        
        data = {
            'device_tokens': [device_token],
            'aps': {
                'alert': message,
                'sound': 'default'
            }
        }
        
        base64string = b64encode('%s:%s' % (UA_APPLICATION_KEY, UA_APPLICATION_MASTER_SECRET))
        headers = {'Authorization': 'Basic %s' % base64string}
        headers.update({'Content-Type': 'application/json'})

        result = urlfetch.fetch(url = url,
            payload = simplejson.dumps(data),
            method = urlfetch.POST,
            headers = headers)
        
        if result.status_code == 200:
            logging.info('Success')
            
            if user_prefs.free_quantity > 0:
                user_prefs.free_quantity = user_prefs.free_quantity - 1
            else:
                user_prefs.paid_quantity = user_prefs.paid_quantity - 1
                
            user_prefs.put()
            
        else:
            logging.error('invalid status code. code: %d' % result.status_code)
            
application = webapp.WSGIApplication(
                                     [('/task/find_device', FindDeviceTask),
                                      ('/task/send_notify', SendNotifyTask)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()