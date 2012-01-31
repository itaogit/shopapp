import logging
import os
from cart import Cart, CartItem
from models import Product
from handlers import BaseHandler
#from webapp2_extras import sessions_memcache
from webapp2_extras import securecookie, security
from google.appengine.api import namespace_manager



class AddToCartHandler(BaseHandler):
    def get(self, subdomain=None):
        #args
        item = self.request.get('item','-')
        qty = int(self.request.get('qty',1))
        
        '''NAMESPACE CHANGE (memcache and datastore)'''
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(subdomain)
        
        '''Name of the memcache'''
        
        self.session = self.session_store.get_session(name='mc_session',max_age=900,backend='memcache')
        #15 mins session (900 secs), if a previous session does not exist it creates a new one
        #self.session = self.session_store.get_session(name='mc_session',max_age=900,backend='memcache')
        
        
        
        try:
            cart = self.session['cart']
            logging.info('cart found in memcache :)')
        except:
            cart = Cart()
            
            logging.info('cart not found in memcache :(')
        #return self.response.write(str(self.session['cart'].__dict__))
        '''import random
        for i in range(1,10):
            product = Product(product_id=i, key_name="test_product_"+str(i),price=round(random.uniform(1,10),2),tax_percent=18.00)
            product.put()
            product.add_stock("test_product_"+str(i),10)'''
        
        
        product = Product.get_by_key_name(item)
        if not product: return self.response.write('The product does not exist')
        elif Product.reserve(item,qty): 
            '''Checked stock'''
            cart.add_item(CartItem(product),qty)
        else:
            self.response.write('Not enough products in the warehouse')
        self.session['cart'] = cart
        
        self.session_store.save_sessions(self.response)
        
        
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write(cart.toString())
        

class RemoveFromCartHandler(BaseHandler):
    def get(self, subdomain=None):
        #args
        item = self.request.get('item','-')
        qty = int(self.request.get('qty',1))
        
        '''NAMESPACE CHANGE (memcache and datastore)'''
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(subdomain)
        
        #15 mins session (900 secs), if a previous session does not exist it creates a new one
        self.session = self.session_store.get_session(name='mc_session',max_age=900,backend='memcache')
        try:
            cart = self.session['cart']
            logging.info('cart found in memcache :)')
        except:
            return self.response.write('Not cart in session or the session has expired')
            
        
        product = Product.get_by_key_name(item)
        
        if not product: return self.response.write('The product does not exist')
        elif Product.unreserve(item,qty):
            '''It was not removed from stock'''
            cart.remove_item(CartItem(product),qty)
        else:
            self.response.write('Some products were not reserved. Probably the session expired')
            
            
        self.session['cart'] = cart
        self.session_store.save_sessions(self.response)
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write(cart.toString())
    
