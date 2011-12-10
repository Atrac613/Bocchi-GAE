# -*- coding: utf-8 -*-

import os
import datetime
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users

from pytz import timezone
import pytz

from db import UserPrefs
from db import DevicePrefs
from db import StoreTweetHistory

os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
# Force Django to reload settings
settings._target = None

from i18NRequestHandler import I18NRequestHandler

class HomePage(I18NRequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                return self.redirect('/user/home')
                
        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/index.html')
        self.response.out.write(template.render(path, template_values))

class TweetPage(I18NRequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                return self.redirect('/user/home')
            
        store_tweet_history = StoreTweetHistory.all().filter('google_account =', user).filter('expired_at >', datetime.datetime.now()).get()
        if store_tweet_history is None:
            can_tweet = True
            expired_at = None
        else:
            can_tweet = False
            user_timezone = timezone(user_prefs.timezone)
            loc_dt = user_timezone.localize(store_tweet_history.expired_at)
            expired_at = loc_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')
                
        template_values = {
            'can_tweet': can_tweet,
            'expired_at': expired_at
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/tweet.html')
        self.response.out.write(template.render(path, template_values))
        
class TweetSuccessPage(I18NRequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                return self.redirect('/user/home')
            
        quantity = user_prefs.free_quantity + user_prefs.paid_quantity
        
        template_values = {
            'quantity': quantity
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/tweet_success.html')
        self.response.out.write(template.render(path, template_values))
        
class BuyPage(I18NRequestHandler):
    def get(self):
        
        template_values = {
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/buy.html')
        self.response.out.write(template.render(path, template_values))

class BuySuccessPage(I18NRequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if user:
            user_prefs = UserPrefs.all().filter('google_account =', user).get()
            if user_prefs is None:
                return self.redirect('/user/home')
            
        quantity = user_prefs.free_quantity + user_prefs.paid_quantity
        
        template_values = {
            'quantity': quantity
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/buy_success.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/store/', HomePage),
                                      ('/store/tweet', TweetPage),
                                      ('/store/tweet/success', TweetSuccessPage),
                                      ('/store/buy', BuyPage),
                                      ('/store/buy/success', BuySuccessPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()