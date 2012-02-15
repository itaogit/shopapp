'''Import section'''
import webapp2
import logging
from models import Product, Shop, Category, Design
from handlers import BaseHandler
from google.appengine.api import namespace_manager
from users import admin_required, login_required
'''End import section'''


class ProductHandler(BaseHandler):
    #@login_required
    def get(self, subdomain):
        namespace_manager.set_namespace(subdomain)
        products = Product.all()
        context = {
                   'url':webapp2.uri_for('addproducts'),
                   'products':products
                   }
        self.render_response('admin-products.html',**context)
    def post(self, subdomain):
        namespace_manager.set_namespace(subdomain)
        visible = False
        if self.request.get('visible') == 'yes':
            visible = True
        name = self.request.get('name')
        categories = self.request.get('category').split(',')
        logging.info(categories)
        cat_refs = []
        for category in categories:
            logging.info(category)
            if Category.get_by_key_name(category):
                cat_refs.append(Category.get_by_key_name(category).key())
        logging.info(cat_refs)
        entity = Product(key_name=name,
                          name=name,
                          shop_id=Shop.get_by_key_name(subdomain),
                          stock=int(self.request.get('qty')),
                          description=self.request.get('description'),
                          price=float(self.request.get('price')),
                          tags=self.request.get('tags').split(','),
                          video=self.request.get('video'),
                          visible=visible,
                          categories=cat_refs
                              )
        entity.put()
        self.redirect(webapp2.uri_for('addproducts'))
        
        
    
class ChangeStyleHandler(BaseHandler):
    
    #@login_required
    def get(self, subdomain):
        namespace_manager.set_namespace(subdomain)
        shop = Shop.all().get()
        designs = Design.all()
        context = {
                   'url':webapp2.uri_for('addproducts'),
                   'designs':designs,
                   'shop':shop,
                   }
        self.render_response('admin-products.html',**context)
    def post(self, subdomain):
        
    