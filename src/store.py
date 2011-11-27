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
from db import StoreTweet

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
            
        store_tweet = StoreTweet.all().filter('google_account =', user).filter('expired_at >', datetime.datetime.now()).get()
        if store_tweet is None:
            can_tweet = True
            expired_at = None
        else:
            can_tweet = False
            expired_at = store_tweet.expired_at
                
        template_values = {
            'can_tweet': can_tweet,
            'expired_at': expired_at
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/store/tweet.html')
        self.response.out.write(template.render(path, template_values))
 
application = webapp.WSGIApplication(
                                     [('/store/', HomePage),
                                      ('/store/tweet', TweetPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()