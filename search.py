'''
Created on 14 Feb 2012

@author: ggarcia
'''
import cgi
import webapp2
import logging
from handlers import BaseHandler, image_linker
from google.appengine.api import namespace_manager
from models import Product


class SearchHandler(BaseHandler):
    def get(self, subdomain):
        '''query'''
        search = self.request.get('search_input')
        
        '''Changing namespace'''
        namespace_manager.set_namespace(subdomain)
        ''''''
        
        query = Product.all().search(search)
        
        context = {'products':query,
                   'imagelinker':image_linker}
        
        self.render_response('search-result.html',**context)