# -*- coding: utf-8 -*- 

import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.api import taskqueue

from django.utils import simplejson 
import base64

from db import UserPrefs
from db import StorePurchaseHistory
from db import StorePurchaseTmpHistory

class VerifyReceiptTask(webapp.RequestHandler):
    def post(self):
        
        receipt_id = self.request.get('id')
        
        store_purchase_tmp_history = StorePurchaseTmpHistory.get_by_id(int(receipt_id))
        if store_purchase_tmp_history is not None:
            receipt_data = store_purchase_tmp_history.receipt_data
            user_prefs = store_purchase_tmp_history.user_prefs
            
            logging.info('Row: %s' % receipt_data)
            
            debug_mode = True
                    
            if debug_mode:
                verify_url = 'https://sandbox.itunes.apple.com/verifyReceipt'
            else:
                verify_url = 'https://buy.itunes.apple.com/verifyReceipt'
            
            receipt_data_b64 = base64.b64encode(receipt_data)
            logging.info('B64: %s' % receipt_data_b64)
            
            payload = simplejson.dumps({'receipt-data': receipt_data_b64}, ensure_ascii=False)
            
            logging.info('Verify URL: %s' % verify_url)
            
            response = urlfetch.fetch(url=verify_url, payload=payload, method=urlfetch.POST, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                result = simplejson.loads(response.content)
                logging.info(response.content)
                if result['status'] == 0:
                    
                    store_purchase_history = StorePurchaseHistory()
                    store_purchase_history.user_prefs = user_prefs.key()
                    store_purchase_history.product_id = result['receipt']['product_id']
                    store_purchase_history.platform = 'ios'
                    store_purchase_history.receipt = response.content
                    store_purchase_history.status = 'pending'
                    store_purchase_history.put()
                    
                    logging.info('Status: Success')
                    
                    store_purchase_tmp_history.status = 'success'
                    store_purchase_tmp_history.put()
                    
                    try:
                        taskqueue.add(url = '/store_api/task/item_count_up', params = {'id': store_purchase_history.key().id()})
                    except:
                        logging.error('Add task failed.')
                        return self.error(500)
                    
                    logging.info('verify receipt success.')
                else:
                    logging.error('Status: Failed')
            else:
                logging.error('ResponseCode: %d' % response.status_code)
                return self.error(500)
                
            logging.info('verify receipt failed.')
        else:
            logging.error('receipt_id not found.')
        
class ItemCountUpTask(webapp.RequestHandler):
    def post(self):
        
        history_id = self.request.get('id')
        
        store_purchase_history = StorePurchaseHistory.get_by_id(int(history_id))
        if store_purchase_history is not None:
            if store_purchase_history.status == 'success':
                return
            
            user_prefs = store_purchase_history.user_prefs
            product_id = store_purchase_history.product_id
            
            send_to = user_prefs.google_account.email()
            
            logging.info('account: %s' % user_prefs.google_account.nickname)
            logging.info('product_id: %s' % product_id)
            
            success = False
            
            if product_id.find('io.atrac613.Bocchi.store.push150') != -1:
                logging.info('product type is push150')
                
                user_prefs.paid_quantity = user_prefs.paid_quantity + 150
                user_prefs.activate_flg = True
                user_prefs.put()
                
                success = True
            else:
                logging.error('unknown product type: %s' % product_id)
                
            if success == True:
                store_purchase_history.status = 'success'
                store_purchase_history.put()
                
            else:
                store_purchase_history.status = 'failed'
                store_purchase_history.put()
        else:
            logging.error('history_id not found.')

application = webapp.WSGIApplication(
                                     [('/store_api/task/verify_receipt', VerifyReceiptTask),
                                      ('/store_api/task/item_count_up', ItemCountUpTask)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
    