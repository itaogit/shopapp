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
        logging.info(str(self.session))
        #cookie_value = self.request.cookies.get('shopapp-cart')
        #logging.info(str(cookie_value))
        '''logging.info(cookie_value)
        if not cookie_value:
            
            #random number
            import random, string
            cookie_value = ''.join(random.choice(string.ascii_uppercase + '123456789') for i in xrange(10))
        self.response.set_cookie(key='shopapp-cart', value=cookie_value,max_age=900)
            
            logging.info(str(self.request.cookies.get('shopapp-cart')))'''
        
        #self.response.set_cookie(key='guille', value='el mejor',max_age=900)
        self.session = self.session_store.get_session(name='shopapp',max_age=None,backend='memcache')
        logging.info(str(self.session))
        #15 mins session (900 secs), if a previous session does not exist it creates a new one
        #self.session = self.session_store.get_session(name='mc_session',max_age=900,backend='memcache')
        #logging.info(cookie_value)
        
        
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
        elif product.reserve(qty): 
            '''Checked stock'''
            cart.add_item(CartItem(product),qty)
        else:
            self.response.write('Not enough products in the warehouse')
        self.session['cart'] = cart
        
        self.session_store.save_sessions(self.response)
        
        
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write(str(cart))
        

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
        elif product.unreserve(qty):
            '''It was not removed from stock'''
            cart.remove_item(CartItem(product),qty)
        else:
            self.response.write('Some products were not reserved. Probably the session expired')
            
            
        self.session['cart'] = cart
        self.session_store.save_sessions(self.response)
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write(str(cart))
    
