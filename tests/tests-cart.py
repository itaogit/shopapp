import unittest
import random
from models import Product
from cart import Cart, CartItem
from google.appengine.api import apiproxy_stub_map,urlfetch_stub
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
class TestProducts(unittest.TestCase):
    
    def setUp(self):
        self.name = random.choice('abc')
        self.product = Product(product_id=random.randint(1,10),key_name=self.name,price=random.uniform(1,10),
                          tax_percent=random.uniform(16,18))
        self.product.put()
        self.stock = random.randint(1,10)
        
        print 'TESTPRODUCTS','Product: ',self.name,' Stock: ', self.stock,
        Product().add_stock(self.name,self.stock)
    def test_reserved(self):
        qty = random.randint(1,10)
        print ' To reserve: ',qty,
        if Product.reserve(self.name,qty):
            p = Product.get_by_key_name(self.name)
            print ' AVAILABLE: ',p.available
            self.assertEqual(p.available, p.stock - qty, 'Not reserving correctly')
        else:
            p = Product.get_by_key_name(self.name)
            print ' Not enough stock', p.available
            self.assertGreater(qty, p.available, 'Not reserving correctly')
        
    def test_stocked(self):
        qty = random.randint(1,10)
    
        print ' To buy: ',qty,
        if Product.reserve(self.name,qty):
            p = Product.get_by_key_name(self.name)
            before = p.reserved
            Product.remove_stock(self.name,qty)
            p = Product.get_by_key_name(self.name)
            print ' AVAILABLE: ',p.available
            self.assertEqual(p.available, p.stock, 'Not lowering stock correctly ')
            self.assertEqual(before - qty,p.reserved, 'Not lowering reserves correctly')
        else:
            p = Product.get_by_key_name(self.name)
            print ' Not enough stock', p.available
            self.assertGreater(qty, p.available, 'Not reserving correctly')
    
'''Test Add to Basket'''
class TestAddToCart(unittest.TestCase):
    
    
    def setUp(self):
        self.products = []
        for i in range(1,10):
            product = Product(product_id=i, key_name="test_product_"+str(i),price=round(random.uniform(1,10),2),tax_percent=18.00)
            product.put()
            product.add_stock("test_product_"+str(i),10)
            self.products.append("test_product_"+str(i))
        self.cart = Cart()
        random.shuffle(self.products)
        
        
    def test_price_cart(self):
        #3 random products in cart
        value = 0.0
        for i in range(3):
            p = Product.get_by_key_name(self.products[i])
            #print p.price,
            value += p.price
            
            self.cart.add_item(CartItem(p),1)
        #print value, self.cart.total_without_tax, self.cart.sub_total_tax, self.cart.sub_total_price, self.cart.total
        self.assertEqual(round(value,2), round(self.cart.total_without_tax,2), 'price not matching')
     
    def test_price_tax_cart(self):   
        value_tax_included = 0.0
        for i in range(3):
            p = Product.get_by_key_name(self.products[i])
            cart_item = CartItem(p)
            qty = random.randint(1,10)
            #qty = 1
            value_tax_included += cart_item.final_price*qty
            self.cart.add_item(cart_item, qty)
        #print value_tax_included, self.cart.total_without_tax, self.cart.sub_total_tax, self.cart.sub_total_price, self.cart.total
        self.assertEqual(round(value_tax_included,2), round(self.cart.sub_total_price,2), 'taxes not being calculated well')
        
        
    def test_reserved_stock(self):
        #3 random products in cart
        value = 0.0
        result = 0
        items_no = 0
        for i in range(3):
            qty = random.randint(1,10)
            print 'product: ', self.products[i], ' to reserve: ',qty,
            if Product.reserve(self.products[i],qty):
                p = Product.get_by_key_name(self.products[i])
                #print p.stock, p.reserved
                self.cart.add_item(CartItem(p),qty)
                result += qty
                items_no +=1
            #p = Product.get_by_key_name(self.products[i])
        print self.cart.total_different_items, items_no
        self.assertEqual(self.cart.total_different_items, items_no, 'Error in total different items')
        self.assertEqual(self.cart.total_items, result, 'Error in total_items')
        
    def test_totals_with_delivery(self):
        print '----------------- TEST AtB TOTALS --------------------'
        
        self.cart.delivery = {'price':2.5,'tax':15.0,'name':'testDelivery'}
        delivery_gross = self.cart.delivery['price'] + self.cart.delivery['price'] * self.cart.delivery['tax']/100
        delivery_tax = self.cart.delivery['price'] * self.cart.delivery['tax'] / 100
        delivery_net = self.cart.delivery['price']
        print 'DELIVERY ','price:', self.cart.delivery['price'], 'plus tax:', delivery_gross, 'tax percent:', self.cart.delivery['tax'],'price tax:', delivery_tax
        
        sub_total_tax_items = 0 #TAX Items
        sub_total_price = 0 #GROSS Items
        total = delivery_gross #GROSS Items + GROSS Delivery
        total_without_tax = delivery_net  #NET Items + NET Delivery
        total_tax =  delivery_tax #TAX items + TAX Delivery
        
        for i in range(3):
            qty = random.randint(1,10)
            
            p = Product.get_by_key_name(self.products[i])
            print self.products[i],'price:', p.price, 'plus tax:', p.price + p.price * p.tax_percent / 100,'tax percent: ',p.tax_percent, 'price tax:',p.price * p.tax_percent / 100, 'qty:',qty
            sub_total_tax_items += (p.price * p.tax_percent / 100)*qty
            sub_total_price +=  (p.price + p.price * p.tax_percent / 100)*qty
            total += (p.price + p.price * p.tax_percent / 100)*qty
            total_without_tax +=  (p.price)*qty
            total_tax += (p.price * p.tax_percent / 100)*qty
            
            self.cart.add_item(CartItem(p),qty)
        
        print 'sub_total_tax_items: ', sub_total_tax_items, ' CART sub_total_tax_items: ',self.cart.sub_total_tax_items
        self.assertEqual(round(sub_total_tax_items,2), round(self.cart.sub_total_tax_items,2), 'Error calculating sub_total_tax_items')
        
        print 'sub_total_price: ', sub_total_price, ' CART sub_total_price: ',self.cart.sub_total_price
        self.assertEqual(round(sub_total_price,2), round(self.cart.sub_total_price,2), 'Error calculating sub_total_price')
        
        print 'total: ', total, ' CART total: ',self.cart.total
        self.assertEqual(round(total,2), round(self.cart.total,2), 'Error calculating total')
        
        print 'total_without_tax: ', total_without_tax, ' CART total_without_tax: ',self.cart.total_without_tax
        self.assertEqual(round(total_without_tax,2), round(self.cart.total_without_tax,2), 'Error calculating total_without_tax')
        
        print 'total_tax: ', total_tax, ' CART total_tax: ',self.cart.total_tax
        self.assertEqual(round(total_tax,2), round(self.cart.total_tax,2), 'Error calculating total_tax')
        print '----------------- END TEST -----------------------' 
        
    
class TestRemoveFromCart(unittest.TestCase):
    
    def setUp(self):
        self.products = []
        self.cart = Cart()
        for i in range(1,10):
            product = Product(product_id=i, key_name="test_product_"+str(i),price=round(random.uniform(1,10),2),tax_percent=18.00)
            product.put()
            product.add_stock("test_product_"+str(i),10)
            self.products.append("test_product_"+str(i))
            p = Product.get_by_key_name("test_product_"+str(i))
            self.cart.add_item(CartItem(p), random.randint(1,10))
        
        random.shuffle(self.products)
        
    
    def test_totals_with_delivery(self):
        print '----------------- TEST RfB TOTALS --------------------'
        
        self.cart.delivery = {'price':2.5,'tax':15.0,'name':'testDelivery'}
        self.cart.recalc()
        delivery_gross = self.cart.delivery['price'] + self.cart.delivery['price'] * self.cart.delivery['tax']/100
        delivery_tax = self.cart.delivery['price'] * self.cart.delivery['tax'] / 100
        delivery_net = self.cart.delivery['price']
        print 'DELIVERY ','price:', self.cart.delivery['price'], 'plus tax:', delivery_gross, 'tax percent:', self.cart.delivery['tax'],'price tax:', delivery_tax
        
        sub_total_tax_items = self.cart.sub_total_tax_items #TAX Items
        sub_total_price = self.cart.sub_total_price #GROSS Items
        total = self.cart.total #GROSS Items + GROSS Delivery
        total_without_tax = self.cart.total_without_tax  #NET Items + NET Delivery
        total_tax =  self.cart.total_tax #TAX items + TAX Delivery
        
        for i in range(3):
            qty = random.randint(1,10)
            qty=1
            p = Product.get_by_key_name(self.products[i])
            print self.products[i],'price:', p.price, 'plus tax:', p.price + p.price * p.tax_percent / 100,'tax percent: ',p.tax_percent, 'price tax:',p.price * p.tax_percent / 100, 'qty:',qty
            sub_total_tax_items -= (p.price * p.tax_percent / 100)*qty
            sub_total_price -=  (p.price + p.price * p.tax_percent / 100)*qty
            total -= (p.price + p.price * p.tax_percent / 100)*qty
            total_without_tax -=  (p.price)*qty
            total_tax -= (p.price * p.tax_percent / 100)*qty
            
            self.cart.remove_item(CartItem(p),qty)
        
        print 'sub_total_tax_items: ', sub_total_tax_items, ' CART sub_total_tax_items: ',self.cart.sub_total_tax_items
        self.assertAlmostEqual(sub_total_tax_items, self.cart.sub_total_tax_items,7, 'Error calculating sub_total_tax_items')
        
        print 'sub_total_price: ', sub_total_price, ' CART sub_total_price: ',self.cart.sub_total_price
        self.assertEqual(round(sub_total_price,2), round(self.cart.sub_total_price,2), 'Error calculating sub_total_price')
        
        print 'total: ', total, ' CART total: ',self.cart.total
        self.assertEqual(round(total,2), round(self.cart.total,2), 'Error calculating total')
        
        print 'total_without_tax: ', total_without_tax, ' CART total_without_tax: ',self.cart.total_without_tax
        self.assertEqual(round(total_without_tax,2), round(self.cart.total_without_tax,2), 'Error calculating total_without_tax')
        
        print 'total_tax: ', total_tax, ' CART total_tax: ',self.cart.total_tax
        self.assertEqual(round(total_tax,2), round(self.cart.total_tax,2), 'Error calculating total_tax')
        print '----------------- END TEST -----------------------' 




