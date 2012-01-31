'''
    ***
    Nothing final yet
    ***

'''
from __future__ import division
import settings
import handlers

from google.appengine.ext import db
    
class Cart():
    '''Object that won't be persistent in the datastore'''
    def __init__(self):
        self.version = settings.CART_VERSION
        self.items = {}
        
        self.country = 'GB'
        self.user_set_country = False
        
        self.delivery = {'price':0.0,'tax':0.0, 'name':'none'} #Another model probably
        self.sub_total_tax_items = 0.0 # Sum of taxes of each item
        self.sub_total_price = 0.0 # Total with TAX
        self.total = 0.0 
        self.total_without_tax = 0.0
        
        self.promo_applied = None
        self.deducted = False
        self.credit_used = 0.0
        
        self.use_gift_voucher = False
        self.credit_used_calced = 0.00
        self.locked = False
        
        self.original_value = 0.00
        self.VAT_RATE = 0.0

    def empty(self):
        self.__init__()
        
    def get_items_list(self):
        return self.items

    def item_in_cart(self,item):
        for i in self.items:
            if i.id == item:
                return True
        return False
    
    def how_many(self,item):
        for i in self.items:
            if i.isbn == item:
                return i.qty
        return 0
    
    
        
    @property
    def total_items(self):
        sum = 0
        for key, item in self.items.items():
            sum += item.qty
        return sum
    @property
    def total_different_items(self):
        return len(self.items)
    @property
    def total_price(self): # Sub Total + Delivery (INCLUDING TAX)
        return self.delivery['price'] + self.sub_total_price
    
    
    @property
    def total_tax(self): #TAX items + TAX delivery
        sum = 0
        for key,item in self.items.items():
            sum += (item.tax_amount)*item.qty
        #It is important those values to be float, if not the division is floored
        sum +=  self.delivery['price'] * self.delivery['tax'] / 100
        return sum
    
    @property
    def total_delivery(self):
        return self.delivery['price'] + self.delivery['price'] * self.delivery['tax'] / 100
    
    def set_country(self, country):
        self.country = country
        self.recalc()
        
    
        
    def add_item(self, item, qty):
        '''item = Item().id --> Product.key().id_or_name()'''
        if self.items.has_key(item.id):
            self.items[item.id].qty += qty
            
        else:
            self.items[item.id] = item
            self.items[item.id].qty = qty
            
        self.recalc()
                  
        
    def change_item_price(self, ref, price):
        self.items[ref].price = price
        self.recalc()
     
    def remove_item(self, item, qty):
        '''item = Item().id --> Product.key().id_or_name()'''
        if self.items.has_key(item.id):
            if qty == 0: del self.items[item.id]
            else:
                self.items[item.id].qty -= qty
                if self.items[item.id].qty <= 0:
                    del self.items[item.id]
            self.recalc()
        
    

    def recalc(self):
        '''Totals section'''
        self.sub_total_tax_items = 0
        self.sub_total_price = 0
        self.total = 0
        self.total_without_tax = 0
        
        for item,value in self.items.items():
            qty = self.items[item].qty
            self.sub_total_tax_items += (self.items[item].tax_amount)*qty #TAX Items
            self.sub_total_price += (self.items[item].final_price)*qty #GROSS Items
            self.total += (self.items[item].final_price)*qty #GROSS Items + GROSS Delivery
            self.total_without_tax += (self.items[item].price)*qty #NET Items + NET Delivery
        #Delivery Section
        self.total += self.total_delivery
        self.total_without_tax = self.total_without_tax + self.delivery['price']
    
    def toString(self):
        chain = ''
        for item,value in self.items.items():
            chain += str(self.items[item].toString)
            #chain += '<br>'+'Product: '+str(self.items[item].id)+' Price: '+str(self.items[item].price)+' Tax: '+str(self.items[item].tax)+' Qty: '+str(self.items[item].qty)+'</br>'
        #Totals
        chain += '<br>Total(Tax inc.): '+str(self.total)+' Tax: '+str(self.total_tax)+'</br>'
        return chain


class CartItem():
    
    def __init__(self, product):
        '''Product() object'''
        self.qty = 0
        self.id = product.key().id_or_name()
        self.price = product.price
        self.tax = product.tax_percent
    
    
    @property
    def final_price(self):
        return self.price + self.price * self.tax / 100
    
    @property
    def tax_amount(self):
        return self.price * self.tax / 100
    
    @property
    def toString(self):
        
        return '<br>'+'Product: '+self.id+' Price: '+str(self.price)+' Tax: '+str(self.tax)+' Qty: '+str(self.qty)+'</br>'
