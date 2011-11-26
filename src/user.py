# -*- coding: utf-8 -*-

import os
import datetime
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

from db import UserPrefs
from db import DevicePrefs
from db import BotPrefs

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from i18NRequestHandler import I18NRequestHandler

class WelcomePage(I18NRequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is not None:
                return self.redirect('/user/home')
                
        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/user/welcome.html')
        self.response.out.write(template.render(path, template_values))

class AuthPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is not None:
            return self.redirect('/user/auth/update')
        
        self.redirect('/user/auth/update?login=false')

class AuthUpdatePage(webapp.RequestHandler):
    def get(self):
        
        login = self.request.get('login')
        
        template_values = {
            'login': login
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/user/auth.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        
        user = users.get_current_user()
        
        device_token = self.request.get('device_token')
        if device_token != '':
            logging.info('device_token: %s' % device_token)
            
            device_prefs = DevicePrefs.all().filter('device_token =', device_token).get()
            if device_prefs is None:
                device_prefs = DevicePrefs()
                device_prefs.google_account = user
                device_prefs.device_token = device_token
                device_prefs.delete_flg = False
                device_prefs.put()
                
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                bot = BotPrefs.all().filter('bot_id =', 'test').get()
                
                user_prefs = UserPrefs()
                user_prefs.google_account = user
                user_prefs.daily_max_notify_count = 3
                user_prefs.paid_quantity = 0
                user_prefs.free_quantity = 100
                user_prefs.timezone = 0.0
                user_prefs.notify_probability = 0.0
                user_prefs.delete_flg = False
                user_prefs.bot_prefs_key = bot.key()
                user_prefs.put()
            
        self.redirect('/user/auth/update?login=true')
        
class HomePage(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        
        user_prefs = UserPrefs.all().filter('google_account =', user).get()
        if user_prefs is None:
            return self.redirect('/user/welcome')
        
        quantity = user_prefs.free_quantity + user_prefs.paid_quantity
        
        max_notify_list = [3, 5, 10, 15, 20]
        
        template_values = {
            'quantity': quantity,
            'user_prefs': user_prefs,
            'max_notify_list': max_notify_list
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/user/home.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        
        user = users.get_current_user()
        
        device_token = self.request.get('device_token')
        if device_token != '':
            logging.info('device_token: %s' % device_token)
            
            device_prefs = DevicePrefs.all().filter('device_token =', device_token).get()
            if device_prefs is None:
                device_prefs = DevicePrefs()
                device_prefs.google_account = user
                device_prefs.device_token = device_token
                device_prefs.delete_flg = False
                device_prefs.put()
                
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                bot = BotPrefs.all().filter('bot_id =', 'test').get()
                
                user_prefs = UserPrefs()
                user_prefs.google_account = user
                user_prefs.daily_max_notify_count = 3
                user_prefs.paid_quantity = 0
                user_prefs.free_quantity = 100
                user_prefs.timezone = 0.0
                user_prefs.notify_probability = 0.0
                user_prefs.delete_flg = False
                user_prefs.bot_prefs_key = bot.key()
                user_prefs.put()
            
            return self.redirect('/user/home')
            
        self.redirect('/user/home')
        
class BotPage(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        
        user_prefs = UserPrefs.all().filter('google_account =', user).get()
        if user_prefs is None:
            return self.redirect('/user/welcome')
        
        
        bot_list = BotPrefs.all().filter('public_flg =', True).fetch(20)
        
        template_values = {
            'bot_list': bot_list,
            'user_prefs': user_prefs
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/user/bot.html')
        self.response.out.write(template.render(path, template_values))
        
application = webapp.WSGIApplication(
                                     [('/user/welcome', WelcomePage),
                                      ('/user/auth', AuthPage),
                                      ('/user/auth/update', AuthUpdatePage),
                                      ('/user/home', HomePage),
                                      ('/user/bot', BotPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()