# -*- coding: utf-8 -*-

import os
import logging
import datetime
import uuid

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import taskqueue

from django.utils import simplejson

from db import UserPrefs
from db import StorePurchaseTmpHistory

class VerifyReceiptAPI(webapp.RequestHandler):
    def post(self):
        
        user = users.get_current_user()
        
        user_prefs = UserPrefs.all().filter('google_account =', user).get()
        if user_prefs is None:
            return self.error(404)
        
        receipt_data = self.request.get('receipt_data')
        logging.info('Row: %s' % receipt_data)
        
        store_purchase_tmp_history = StorePurchaseTmpHistory()
        store_purchase_tmp_history.user_prefs = user_prefs.key()
        store_purchase_tmp_history.platform = 'ios'
        store_purchase_tmp_history.receipt_data = receipt_data
        store_purchase_tmp_history.status = 'pending'
        store_purchase_tmp_history.secret_key = uuid.uuid4().hex
        store_purchase_tmp_history.put()
        
        try:
            taskqueue.add(url = '/store_api/task/verify_receipt', params = {'id': store_purchase_tmp_history.key().id()})
        
            json = simplejson.dumps({'status': True, 'key': store_purchase_tmp_history.secret_key}, ensure_ascii=False)
            self.response.content_type = 'application/json'
            return self.response.out.write(json)
            
        except:
            logging.error('Add task failed.')
        
        json = simplejson.dumps({'status': False, 'key': None}, ensure_ascii=False)
        self.response.content_type = 'application/json'
        self.response.out.write(json)

class ReceiptStatusAPI(webapp.RequestHandler):
    def post(self):
        secret_key = self.request.get('key')
        
        store_purchase_tmp_history = StorePurchaseTmpHistory.all().filter('secret_key =', secret_key).get()
        if store_purchase_tmp_history is not None:
            if store_purchase_tmp_history.status == 'pending':
                json = simplejson.dumps({'pending': True}, ensure_ascii=False)
            else:
                json = simplejson.dumps({'pending': False}, ensure_ascii=False)
                
            logging.info('Result: %s' % json)
            self.response.content_type = 'application/json'
            self.response.out.write(json)
        else:
            self.error(404)
        
application = webapp.WSGIApplication(
                                     [('/store_api/verify_receipt', VerifyReceiptAPI),
                                      ('/store_api/receipt_status', ReceiptStatusAPI)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()