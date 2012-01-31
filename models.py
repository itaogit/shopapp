#Better performance of json in Python 2.7
import json
import webapp2
import google.appengine.api.images
from google.appengine.ext import db

class Shop(db.Model):
    shopname = db.StringProperty()
    owner = db.ReferenceProperty() #User Reference
    times_visited = db.IntegerProperty()
    currency = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    '''Editable Features'''
    logo = db.BlobProperty()
    description = db.TextProperty()
    pricing_plan = db.StringProperty() #Needs clarification
    address = db.PostalAddressProperty()
    email = db.EmailProperty()
    main_phone_number = db.PhoneNumberProperty()
    secondary_phone_number = db.PhoneNumberProperty()
    
    '''Google Checkout Credentials'''
    google_merchant_id = db.StringProperty(default=None)
    google_merchant_key = db.StringProperty(default=None)
    '''Authorize Credentials'''
    authorize_login_id = db.StringProperty(default=None)
    authorize_trans_key = db.StringProperty(default=None)
    '''Sagepay Credentials'''
    sagepay_live_mer = db.StringProperty(default=None)
    sagepay_live_ven = db.StringProperty(default=None)
    sagepay_live_trans_key = db.StringProperty(default=None)
    '''Paypal Credentials'''
    paypal_username = db.StringProperty(default=None)
    paypal_password = db.StringProperty(default=None)
    paypal_signature = db.StringProperty(default=None)




'''Style/Template configuration, more models'''
'''Customized CSS
    Template Style
    Replaceable Images
    
'''

   


class Category(db.Model):
    categoryname = db.StringProperty(required=True)
    description = db.TextProperty()
    
    '''JSON OBJECT
       # * [{'1':3},{'2':5},(...)] --> Meaning: 1 object, $3; 2 objects, $5 
       # * It needs of serialization and deserealization before storing and getting operations
    '''
    _price_of_delivery = db.StringProperty() #it probably needs discussion
    
    
    @property
    def products(self):
        ''' Category - Product (Many to Many relationship)'''
        return Product.gql("WHERE categories IN :1", self.key())
    
    def set_delivery(self, delivery_dict):
        self._price_of_delivery = json.dumps(delivery_dict)
    def get_delivery(self):
        return json.loads(self._price_of_delivery)

class Product(db.Expando):
    '''The properties of an Expando class are dynamic and can be added in runtime'''
    
    shop_id = db.ReferenceProperty()
    
    name = db.StringProperty()
    description = db.TextProperty()
    price = db.FloatProperty()
    tax_percent = db.FloatProperty()
    tax_code = db.StringProperty()
    '''List of blobs, BlobStore can't be associated with namespaces
       * The filtering has to be done at DataStore level
    '''
    images = db.ListProperty(db.BlobKey)
    tags = db.StringListProperty()
    
    '''STOCK'''
    stock = db.IntegerProperty(default=0)
    reserved = db.IntegerProperty(default=0)
    
    '''JSON OBJECT
        * [{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']},(...)]
        * It needs of serialization and deserealization before storing and getting operations
    '''
    options = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    visible = db.BooleanProperty(default=False)
    ''' Category - Product (Many to Many relationship)'''
    categories = db.ListProperty(db.Key)
    
    
    
    #options (private variable)
    def set_options(self, name, data):
        def txn():
            instance = self.get_by_key_name(name)
            instance._options = json.dumps(data)
            instance.put()
        return db.run_in_transaction(txn)
    def get_options(self, name):
        instance = self.get_by_key_name(name)
        return json.loads(instance._options)
        
    
    #stock access
    @classmethod
    def add_stock(cls,name,qty):
        instance = cls.get_by_key_name(name)
        instance.stock +=  qty
        instance.put()
    @classmethod
    def remove_stock(self,name,qty):
        def txn():
            instance = self.get_by_key_name(name)
            if qty > instance.stock: 
                #Stock insufficient
                return False
            else:
                instance.reserved -= qty 
                instance.stock -= qty
                instance.put()
                return True
        return db.run_in_transaction(txn)
    @classmethod
    def reserve(self,name,qty):
        def txn():
            instance = self.get_by_key_name(name)
            
            if (instance.stock - instance.reserved - qty) >= 0:
                
                instance.reserved += qty
                instance.put()
                return True
            else:
                return False
        return db.run_in_transaction(txn)
    
    @classmethod
    def unreserve(self,name,qty):
        def txn():
            instance = self.get_by_key_name(name)
            if instance.reserved >= qty:
                instance.reserved -= qty
                
                instance.put()
                return True
            else:
                instance.reserved = 0
                instance.put()
                return True
            return False
        return db.run_in_transaction(txn)
    @property
    def available(self,name):
        instance = self.get_by_key_name(name)
        return instance.stock - instance.reserved
    #price
    @property
    def total_price(self, name):
        instance = self.get_by_key_name(name)
        return instance.price + instance.price * instance.tax_percent /100
    
    #tagging
    def set_tag(self,name, data, index):
        def txn():
            instance = self.get_by_key_name(name)
            instance.tags[index] = data
            instance.put()
        return db.run_in_transaction(txn)
    
    #Image access
    def add_image(self,name, blob_key, index):
        def txn():
            instance = self.get_by_key_name(name)
            instance.images[index] = blob_key
            instance.put()
        return db.run_in_transaction(txn)
    def delete_image(self,name, index):
        def txn():
            instance = self.get_by_key_name(name)
            del instance.images[index]
            instance.put()
        return db.run_in_transaction(txn)
        
    def get_image(self,name, index, size=None):
        instance = self.get_by_key_name(name)
        return get_serving_url(instance.images[index], size)
    
    def get_images(self,name, size=None):
        serving_urls = []
        instance = self.get_by_key_name(name)
        for k in instance.images:
            serving_urls.append(get_serving_url(k, size))
        return serving_urls
    
    
    def set_new_price(self,name, price):
        def txn():
            instance = self.get_by_key_name()
            instance.price = price
            instance.put()
        return db.run_in_transaction(txn)
    
    def set_description(self,name, description):
        def txn():
            instance = self.get_by_key_name(name)
            instance.description = description
            instance.put()
        return db.run_in_transaction(txn)
    
    #categories
    def add_to_category(self, cat):
        '''cat = key() !!'''
        if cat not in self.categories:
            self.categories.append(cat)
    
    def remove_from_category(self, cat):
        '''cat = key() !!'''
        if cat in self.categories:
            self.categories.remove(cat)
    
    @staticmethod
    def get_by_name(cls,n):
        return cls.get_by_key_name(n)

    

''' Order Model represents a users purchase '''
class Order(db.Model):
    #cart = db.StringProperty()
    
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    #user = db.ReferenceProperty(User)
    total = db.IntegerProperty()
    sessionno = db.StringProperty()
    total_price = db.FloatProperty() 
    status = db.StringProperty(default='Placed')
    delivery_address = db.PostalAddressProperty()
    billing_address = db.PostalAddressProperty()
    payment_method = db.StringProperty()
    delivery_price = db.FloatProperty()
    delivery_name = db.StringProperty()
    cart_key = db.StringProperty() #Comes from the session
    promo_code = db.StringProperty()
    
    
    
    @classmethod
    def get_or_insert_with_flag(cls, key_name, **kwds):
        def txn():
            new = False
            entity = cls.get_by_key_name(key_name)
            if entity is None:
                new = True
                entity = cls.create(key_name=key_name, **kwds)
                cls.generate_details(parent=key_name, stored_cart=cart_key)
                entity.put()
            return (entity, new)
        return run_in_transaction(txn)
    
    @classmethod
    def last_order(cls):
        query = cls.all(keys_only=True)
        query.order('-created')
        return query.get()
    
    @property
    def order_no(self):
        return self.key().id_or_name()
    
    
    @classmethod
    def get_by_user(cls,user):
        orders = cls.all()
        orders.filter("user =", user)
        return orders
      
    @classmethod
    def confirm(cls, cart):
        '''Order placed, normally after order.put()'''
        pass
    
    @classmethod
    def get_by_date(cls,date_from=None,date_to=None):
        query = cls.all()
        if date_from: query.filter('created >', date_from) 
        if date_to: query.filter('created <',date_to)
        query.order('-created')
        return query

class OrderDetail(db.Model):
    order_no = db.StringProperty()
    payment_method = db.StringProperty()
    user = db.StringProperty()
    created = db.DateTimeProperty()
    isbn = db.StringProperty()
    category = db.StringListProperty()
    author = db.StringProperty()
    price_before_tax = db.FloatProperty()
    tax_price = db.FloatProperty()
    status = db.StringProperty() #CHARGED OR VOUCHER
    promo_code = db.StringProperty()
    qty = db.IntegerProperty()
    country = db.StringProperty()
    
    
    @property
    def total_price(self):
        return self.price_before_tax + self.tax_price
  
class Image(db.Model):
    blob_key = db.StringProperty()
    user = db.StringProperty()

class Item(db.Model):
    name = db.StringProperty()
    qty = db.IntegerProperty()
