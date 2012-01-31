import json
import google.appengine.api.images
from google.appengine.ext import db


class Homepage(db.Expando):
    template = db.StringProperty()
    '''JSON OBJECT
       # * [{'1':(256,256,0)},{'2':(256,0,100)},(...)] --> Meaning: (RED, BLUE, GREEN)
       # * It needs of serialization and deserealization before storing and getting operations
    '''
    _colour_conf = db.StringProperty()
    
    
    
    
    @classmethod
    def set_colour_conf(cls, delivery_dict):
        '''[{'1':(256,256,0)},{'2':(256,0,100)},(...)]'''
        cls._colour_conf = json.dumps(delivery_dict)
    @classmethod
    def get_colour_conf(cls):
        return json.loads(cls._colur_conf)
        
    
    
    
    
class Productpage(db.Expando):
    template = db.StringProperty()
    '''JSON OBJECT
       # * [{'1':(256,256,0)},{'2':(256,0,100)},(...)] --> Meaning: (RED, BLUE, GREEN)
       # * It needs of serialization and deserealization before storing and getting operations
    '''
    _colour_conf = db.StringProperty()
    
    
    
    
    @classmethod
    def set_colour_conf(cls, delivery_dict):
        '''[{'1':(256,256,0)},{'2':(256,0,100)},(...)]'''
        cls._colour_conf = json.dumps(delivery_dict)
    @classmethod
    def get_colour_conf(cls):
        return json.loads(cls._colur_conf)