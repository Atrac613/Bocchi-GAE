# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# db entities
# ------------------------------------------------------------------------------

from google.appengine.ext import db

class BotPrefs(db.Model):
    google_account = db.UserProperty()
    bot_id = db.StringProperty()
    nickname = db.StringProperty()
    public_flg = db.BooleanProperty()
    delete_flg = db.BooleanProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=True)
    
class UserPrefs(db.Model):
    google_account = db.UserProperty()
    daily_max_notify_count = db.IntegerProperty()
    schedule_0000_0300 = db.BooleanProperty()
    schedule_0300_0600 = db.BooleanProperty()
    schedule_0600_0900 = db.BooleanProperty()
    schedule_0900_1200 = db.BooleanProperty()
    schedule_1200_1500 = db.BooleanProperty()
    schedule_1500_1800 = db.BooleanProperty()
    schedule_1800_2100 = db.BooleanProperty()
    schedule_2100_2400 = db.BooleanProperty()
    timezone = db.FloatProperty()
    free_quantity = db.IntegerProperty()
    paid_quantity = db.IntegerProperty()
    bot_prefs_key = db.ReferenceProperty(BotPrefs)
    schedule_list = db.ListProperty(int)
    notify_probability = db.FloatProperty()
    delete_flg = db.BooleanProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=True)
    
class DevicePrefs(db.Model):
    device_token = db.StringProperty()
    google_account = db.UserProperty()
    delete_flg = db.BooleanProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=True)
    
class BotMessage(db.Model):
    bot_prefs_key = db.ReferenceProperty(BotPrefs)
    time = db.StringProperty()
    message = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=True)
    
class StoreTweet(db.Model):
    google_account = db.UserProperty()
    expired_at = db.DateTimeProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=True)
    