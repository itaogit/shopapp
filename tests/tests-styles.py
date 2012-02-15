'''
Created on 15 Feb 2012

@author: ggarcia
'''
import unittest
import random
from models import Product, Shop, Design
from cart import Cart, CartItem
from google.appengine.api import apiproxy_stub_map,urlfetch_stub, namespace_manager
import os, sys, glob 
from os.path import dirname, basename, splitext, join


app_id = 'itaoshoptest'
os.environ['APPLICATION_ID'] = app_id
datastore_file = '/dev/null'
from google.appengine.api import apiproxy_stub_map,datastore_file_stub
apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
stub = datastore_file_stub.DatastoreFileStub(app_id, datastore_file, '/')
apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)



'''Test Class Products'''
class TestStyles(unittest.TestCase):

    def setUp(self):
        self.design = Design(css_product='product.css', css_home='qshops-home.css', home_template='qshops-home.html', product_template='product.html')
        self.design.put()
        namespace_manager.set_namespace('b')
        self.shop = Shop().all().get()
        self.shop.design = self.design
        self.shop.put()
        
    def test_reserved(self):
       namespace_manager.set_namespace('b')
       self.assertTrue(True, 'Not reserving correctly') 
                
        
        
        
        