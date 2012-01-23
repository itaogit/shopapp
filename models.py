from google.appengine.ext import db


class Shop(db.Model):
    shopname = db.StringProperty()
    owner = db.ReferenceProperty()
    times_visited = db.IntegerProperty()
    
    
class Item(db.Model):
    name = db.StringProperty()
    qty = db.IntegerProperty()
    
    
    
