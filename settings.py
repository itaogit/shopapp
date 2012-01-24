import os
from google.appengine.api import app_identity




app_id = app_identity.get_application_id()
#DOMAIN = app_id + '.appspot.com'
DOMAIN = 'localhost:8091'



CART_VERSION = 1