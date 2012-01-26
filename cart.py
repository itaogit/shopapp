'''
    ***
    Nothing final yet
    ***

'''
from __future__ import division
import handlers
from google.appengine.ext import db
    
class Cart():
    '''Object that won't be persistent in the datastore'''
    def __init__(self):
        self.version = settings.CART_VERSION
        self.items = {}
        
        self.country = 'GB'
        self.user_set_country = False
        self.sub_total_price = 0.0 # Total with TAX
        self.delivery = {'price':0.0, 'name':'none'}
        self.sub_total_tax = 0.0 # Sum of taxes of each item
        self.total = 0.0 
        self.total_without_tax = 0.0
        self.all_ok = True
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
        return len(self.items)
    
    @property
    def total_price(self): # Sub Total + Delivery (INCLUDING TAX)
        return self.delivery['price'] + self.sub_total_price
    
    
    @property
    def total_tax(self):
        sum = 0
        for i in self.items:
            sum += i.tax
        #It is important those values to be float, if not the division is floored
        sum +=  self.delivery['price'] / (100+self.VAT_RATE) * self.VAT_RATE
        return sum
    

    def set_country(self, country):
        self.country = country
        self.recalc()
        
    
        
    def add_item(self, item, qty):
        '''item = Item().id --> Product.key().id_or_name()'''
        if self.items.has_key(item.id):
            self.items[item.id].qty += qty
        else:
            self.items[item.id] = item
        self.recalc()
    
               
        
    def remove_vat(self,ref):
        self.items[ref].vat = 0.00
        self.recalc()
        
    def change_item_price(self, ref, price):
        self.items[ref].price = price
        self.recalc()
     
    def remove_item(self, ref):
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.voucher = None
        del self.items[ref]
        self.recalc()
        
    def remove_item_by_id(self, id):
        
        for i in self.items:
            if i.id == str(id):
                self.items.remove(i)
        
        self.recalc()

    def recalc(self):
        #To implement
        pass
    


class CartItem():
    
    def __init__(self, product):
        '''Product() object'''
        self.qty = 1
        self.id = product.key().id_or_name()
        self.price = product.price
        self.tax = product.tax
        
    @classmethod
    def final_price(cls):
        return product.final_price

