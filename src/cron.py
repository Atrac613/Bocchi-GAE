# -*- coding: utf-8 -*-

import os
import logging
import datetime
import random

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import taskqueue
from google.appengine.api import memcache

from db import UserPrefs

class NotifyCron(webapp.RequestHandler):
    def get(self):
        
        page_id = self.request.get('page_id')
        if page_id != '':
            page_id = int(page_id)
        else:
            page_id = 1
            
        user_list_query = UserPrefs.all().filter('schedule_list =', datetime.datetime.now().hour)
        
        last_cursor = memcache.get('notify_cursor_%d' % page_id)
        if last_cursor:
            user_list_query.with_cursor(last_cursor)
        
        user_list = user_list_query.fetch(1)
        if user_list is not None:
            logging.info('count: %d' % len(user_list))
            for user in user_list:
                rand = random.random() * 100
                #rand = 0
                logging.info('random: %f, probability: %f' % (rand, user.notify_probability))
                if rand < user.notify_probability:
                    logging.info('Add notify task.')
                    try:
                        #bot_id=1
                        bot_id = user.bot_prefs_key.key().id()
                        taskqueue.add(url = '/task/find_device', params = {'user_id': user.key().id(), 'bot_id': bot_id})
                    except:
                        logging.error('Add task failed.')
                else:
                    logging.info('Boo...')
            
        cursor = user_list_query.cursor()
        
        user_list_query = UserPrefs.all().filter('schedule_list =', datetime.datetime.now().hour)
        user_list_query.with_cursor(cursor)
        user_list = user_list_query.fetch(1)
        logging.info('count: %d' % len(user_list))
        if memcache.get('notify_cursor_%d' % (page_id+1)):
            memcache.delete('notify_cursor_%d' % (page_id+1))
            
        memcache.add('notify_cursor_%d' % (page_id+1), cursor, 30)
        
        if len(user_list) <= 0:
            next_page_id = None
        else:
            next_page_id = page_id + 1
            logging.info('recursive...')
            try:
                taskqueue.add(url = '/cron/notify', params = {'page_id': next_page_id}, method='GET')
            except:
                logging.error('Add task failed.')
        
application = webapp.WSGIApplication(
                                     [('/cron/notify', NotifyCron)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()