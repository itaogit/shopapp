import logging
from cart import Cart, CartItem
from models import Product
from handlers import BaseHandler
from webapp2_extras import sessions_memcache



class AddToCartHandler(BaseHandler):
    def get(self, subdomain=None):
        #args
        item = self.request.get('item','')
        qty = self.request.get('qty',0)
        
        '''NAMESPACE CHANGE (memcache and datastore)'''
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(subdomain)
        
        user = '' #Logged user
        
        #15 mins session (900 secs), if a previous session does not exist it creates a new one
        self.session = self.session_store.get_session(name=user+'_mc_session',max_age=60,backend='memcache')
        try:
            cart = self.session['cart']
            logging.info('cart found in memcache :)')
        except:
            cart = Cart()
            logging.info('cart not found in memcache :(')
        
        
        
        product = Product.get_by_name(item)
        if not product: return self.response.write('The product does not exist')
        else: cart.add_item(CartItem(product),qty)
        
        self.session['cart'] = cart
        
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write('Saved!!')

class RemoveFromCartHandler(BaseHandler):
    def get(self, subdomain=None):
        #args
        item = self.request.get('item','')
        qty = self.request.get('qty',0)
        
        '''NAMESPACE CHANGE (memcache and datastore)'''
        namespace = namespace_manager.get_namespace()
        namespace_manager.set_namespace(subdomain)
        
        #15 mins session (900 secs), if a previous session does not exist it creates a new one
        self.session = self.session_store.get_session(name='_mc_session',max_age=60,backend='memcache')
        try:
            cart = self.session['cart']
            logging.info('cart found in memcache :)')
        except:
            return self.response.write('Not cart in session or the session has expired')
            
        
        product = Product.get_by_name(item)
        
        if not product: return self.response.write('The product does not exist')
        else: cart.remove_item(CartItem(product),qty)
        
        self.session['cart'] = cart
        
        '''NAMESPACE CHANGE'''
        namespace_manager.set_namespace(namespace)
        
        return self.response.write('Saved!!') 