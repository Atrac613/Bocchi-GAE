# -*- coding: utf-8 -*-

import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users

from db import BotMessage
from db import BotPrefs

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from i18NRequestHandler import I18NRequestHandler

class HomePage(I18NRequestHandler):
    def get(self):

        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/index.html')
        self.response.out.write(template.render(path, template_values))

class ListPage(I18NRequestHandler):
    def get(self):
        user = users.get_current_user()
        
        bot_list = BotPrefs.all().filter('google_account =', user).fetch(20)

        template_values = {
            'bot_list': bot_list
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/list.html')
        self.response.out.write(template.render(path, template_values))

class EditPage(I18NRequestHandler):
    def get(self):

        bot_id = self.request.get('bot_id')
        
        bot_prefs = BotPrefs.all().filter('bot_id =', bot_id).get()
        if bot_prefs is None:
            return self.error(404)
        
        template_values = {
            'bot_id': bot_id,
            'nickname': bot_prefs.nickname,
            'public_flg': bot_prefs.public_flg,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/edit.html')
        self.response.out.write(template.render(path, template_values))

class ScheduleListPage(I18NRequestHandler):
    def get(self):

        bot_id = self.request.get('bot_id')
        
        bot_prefs = BotPrefs.all().filter('bot_id =', bot_id).get()
        if bot_prefs is None:
            return self.error(404)
        
        advance_flg = self.request.get('advance')
        if advance_flg == 'True':
            advance_flg = True
        else:
            advance_flg = False
        
        schedule_list = []
        
        if advance_flg:
            for i in range(24):
                time_key = '%02d00-%02d00' % (i, i+1)
                time = '%02d:00 - %02d:00' % (i, i+1)
                bot_message_list = BotMessage.all().filter('bot_prefs_key =', bot_prefs.key()).filter('time =', time_key).order('created_at').fetch(20)
                
                schedule_list.append({'time':time, 'list': bot_message_list, 'hour': 0})
        else:
            for i in [0, 3, 6, 9, 12, 15, 18, 21]:
                time = '%02d:00 - %02d:00' % (i, i+3)
                
                hour = i
                bot_message_list = []
                message_list = []
                for n in range(3):
                    time_key = '%02d00-%02d00' % (hour, hour+1)
                    bot_message = BotMessage.all().filter('bot_prefs_key =', bot_prefs.key()).filter('time =', time_key).order('created_at').fetch(20)
                    
                    for row in bot_message:
                        if row.message not in message_list:
                            bot_message_list.append(row)
                            message_list.append(row.message)
                    
                    hour = hour + 1
                    
                schedule_list.append({'time':time, 'list': bot_message_list, 'hour': i})

        
        template_values = {
            'bot_id': bot_id,
            'nickname': bot_prefs.nickname,
            'public_flg': bot_prefs.public_flg,
            'schedule_list': schedule_list,
            'advance_flg': advance_flg
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/schedule_list.html')
        self.response.out.write(template.render(path, template_values))

class AddMessagePage(I18NRequestHandler):
    def get(self):

        bot_id = self.request.get('bot_id')
        
        bot_prefs = BotPrefs.all().filter('bot_id =', bot_id).get()
        if bot_prefs is None:
            return self.error(404)
        
        advance_flg = self.request.get('advance')
        if advance_flg == 'True':
            advance_flg = True
        else:
            advance_flg = False
        
        hour_list = []
        if advance_flg:
            for i in range(24):
                key = '%02d00-%02d00' % (i, i+1)
                value = '%02d:00 - %02d:00' % (i, i+1)
                logging.info('%s'%value)
                hour_list.append({'key':key, 'value':value})
            
        else:
            for i in [0, 3, 6, 9, 12, 15, 18, 21]:
                key = 'simple_%d' % i
                value = '%02d:00 - %02d:00' % (i, i+3)
                logging.info('%s'%value)
                hour_list.append({'key':key, 'value':value})
        
        template_values = {
            'hour_list': hour_list,
            'bot_id': bot_id,
            'advance_flg': advance_flg
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/add_message.html')
        self.response.out.write(template.render(path, template_values))
    
class ShowMessagePage(I18NRequestHandler):
    def get(self):
        
        user= users.get_current_user()
        
        id = self.request.get('id')
        bot_id = self.request.get('bot_id')
        
        bot_prefs = BotPrefs.all().filter('google_account =', user).filter('bot_id =', bot_id).get()
        if bot_prefs is None:
            return self.error(404)
        
        bot_message = BotMessage.get_by_id(int(id))
        if bot_message is None:
            return self.error(404)
        
        if bot_message.bot_prefs_key.key() != bot_prefs.key():
            return self.error(404)
        
        advance_flg = self.request.get('advance')
        if advance_flg == 'True':
            advance_flg = True
        else:
            advance_flg = False
            
        hour = self.request.get('hour')
        try:
            hour = int(hour)
        except:
            hour = 0
        
        template_values = {
            'bot_message': bot_message,
            'bot_id': bot_id,
            'advance_flg': advance_flg,
            'hour': hour
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/show_message.html')
        self.response.out.write(template.render(path, template_values))
    
class AddPage(I18NRequestHandler):
    def get(self):

        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/bot/add.html')
        self.response.out.write(template.render(path, template_values))
    
application = webapp.WSGIApplication(
                                     [('/bot/', HomePage),
                                      ('/bot/add', AddPage),
                                      ('/bot/list', ListPage),
                                      ('/bot/edit', EditPage),
                                      ('/bot/schedule_list', ScheduleListPage),
                                      ('/bot/add_message', AddMessagePage),
                                      ('/bot/show_message', ShowMessagePage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()