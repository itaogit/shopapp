import os
from google.appengine.api import app_identity



try:
    app_id = app_identity.get_application_id()
except:
    app_id = 'itaoshoptest'
#DOMAIN = app_id + '.appspot.com'
DOMAIN = 'localhost:8091'



CART_VERSION = 1