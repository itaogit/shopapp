#Better performance of json in Python 2.7
import json
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
    tax_percent = db.FloatProperty()
    '''JSON OBJECT
        * [{'1':3},{'2':5},(...)] --> Meaning: 1 object, £3; 2 objects, £5 
        * It needs of serialization and deserealization before storing and getting operations
    '''
    _price_of_delivery = db.StringProperty() #it probably needs discussion
    
    
    @property
    def products(self):
        ''' Category - Product (Many to Many relationship)'''
        return Contact.gql("WHERE categories = :1", self.key())
    
    def set_delivery(self, delivery_dict):
        self._price_of_delivery = json.dumps(delivery_dict)
    def get_delivery(self):
        return json.loads(self._price_of_delivery)

class Product(db.Expando):
    '''The properties of an Expando class are dynamic and can be added in runtime'''
    productname = db.StringProperty(required=True)
    shop_id = db.ReferenceProperty(required=True)
    
    name = db.StringProperty()
    description = db.TextProperty()
    price = db.FloatProperty()
    '''List of blobs, BlobStore can't be associated with namespaces
       * The filtering has to be done at DataStore level
    '''
    images = db.ListProperty(db.Blob)
    tags = db.StringListProperty()
    stock = db.IntegerProperty()
    '''JSON OBJECT
        * [{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']},(...)]
        * It needs of serialization and deserealization before storing and getting operations
    '''
    _options = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    visible = db.BooleanProperty(default=False)
    ''' Category - Product (Many to Many relationship)'''
    categories = db.ListProperty(db.Key)
    
    #options (private variable)
    def set_options(self, data):
        self._options = json.dumps(data)
    def get_options(self):
        return json.loads(self._options)
    
    #stock access
    def add_stock(self,qty):
        self.stock += qty
    def remove_stock(self,qty):
        if qty > self.stock: raise ValueError, "Stock insuficient"
        else: self.stock -= qty
    
    #tagging
    def set_tag(self, data, index):
        self.tags[index] = data
    
    #Image access
    def add_image(self, blob_image, index):
        self.images[index] = data
    def get_image(self, index):
        return self.images[index]
    def get_images(self):
        return self.images
    
    def set_new_price(self, price):
        self.price = price
    
    
    def set_description(self, description):
        self.description = description
    
    #categories
    def add_to_category(self, cat):
        '''cat = key() !!'''
        if cat not in self.categories:
            self.categories.append(cat)
    
    def remove_from_category(self, cat):
        '''cat = key() !!'''
        if cat in self.categories:
            self.categories.remove(cat)
    

''' Order Model represents a users purchase '''
class Order(db.Model):
    #cart = db.StringProperty()
    
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    user = db.ReferenceProperty(User)
    total = db.IntegerProperty()
    sessionno = db.StringProperty()
    total_price = db.FloatProperty() 
    status = db.StringProperty(default='Placed')
    delivery_address = db.PostalAddressProperty()
    billing_address = db.PostalAddressProperty()
    payment_method = db.StringProperty()
    delivery_price = db.FloatProperty()
    delivery_name = db.StringProperty()
    cart_key = db.StringProperty()
    promo_code = db.StringProperty()
    
    @propery
    def order_no(self):
        return self.key()
    
    @classmethod
    def get_all(cls):
        orders = cls.all()
        return orders
    
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
    price_after_tax = db.FloatProperty()
    status = db.StringProperty() #CHARGED OR VOUCHER
    promo_code = db.StringProperty()
    qty = db.IntegerProperty()
    country = db.StringProperty()

    
class Image(db.Model):
    blob_key = db.StringProperty()
    user = db.StringProperty()

