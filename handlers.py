'''Import section'''
import webapp2
import main
import logging
from webapp2_extras import jinja2
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import images
from models import Shop, Product, Image, Item
from google.appengine.api import namespace_manager
from google.appengine.api import memcache
'''End import section'''

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

class PageHandler(BaseHandler):
    def get(self, page='home'):
        context = {
            'title': page,
            'stylesheet': None,
            'pagecontent': 'this is the ' + page + ' page',
        }
        self.render_response('qshops-home.html', **context)


class CreateShopHandler(BaseHandler):
    def get(self, subdomain):
        '''Saving current namespace'''
        namespace = namespace_manager.get_namespace()
        '''Changing the namespace'''
        namespace_manager.set_namespace(subdomain)
        '''The following query only look into the current namespace'''
        query = Shop.all().filter('shopname',subdomain).get()
        if query is None:
            entity = Shop(key_name=subdomain, shopname=subdomain, times_visited=0)
            entity.put()
            '''
                We set the previous namespace back
            '''
            namespace_manager.set_namespace(namespace)
            self.response.write('Shop created')
        else:
            self.response.write('The shop already exists')
            

class AddItemHandler(BaseHandler):
    def get(self, subdomain, item, qty):
        namespace_manager.set_namespace(subdomain)
        entity = Item(key_name=item, name=item, qty=int(qty))
        entity.put()
        self.response.write('Done') 

class ShoppingAreaHandler(BaseHandler):
    def get(self, subdomain, to_cache):
        logging.info(subdomain)
        '''Saving current namespace'''
        namespace = namespace_manager.get_namespace()
        '''Changing the namespace'''
        namespace_manager.set_namespace(subdomain)
        
        '''MEMCACHE OF THE NAMESPACE'''
        data = memcache.get('lastopinion')
        if data:
            to_write = 'The last buyer said: <blockquote>%s</blockquote>' %data
            if not memcache.set('lastopinion',to_cache):
                to_write = 'A cache error happened :('
                pass
            
        else:
            to_write = 'We have not stored what the last buyer said'
            if not memcache.add('lastopinion',to_cache):
                to_write = 'A cache error happened 2 :('
            
        
        query = Item.all().fetch(10)
        to_write += '<br>Items in this shop</br>'
        for i in query:
            to_write += '<blockquote>item: %s qty: %s</blockquote>' %(i.name,i.qty)
        
        namespace_manager.set_namespace(namespace)
        self.response.write(to_write)

class SiteHandler(BaseHandler):
    def get(self, subdomain):
        #site_name = SUBDOMAIN_RE.search(self.request.host).group(1)
        
        context = {}
        logging.info('SiteHandler')
        '''Make sure the access is only granted to those resources in the namespace'''
        self.set_current_namespace(subdomain)
        
        '''Check whether the site exists or not'''
        
        #site = Shop.get_by_key_name(subdomain)
        #if not site:
        if not subdomain in ['a','b','c','www']:
            
            return self.render_response('not-found.html', **context)
        
        if subdomain == 'a':
            stylesheet = 'blue'
        elif subdomain == 'b':
            stylesheet = 'red'
        elif subdomain == 'c':
            stylesheet = 'green'
        else:
            stylesheet = 'default'
        
        context = {
                'title': subdomain,
                'pagecontent': 'this is the ' + subdomain + ' page',
                #'stylesheet': site.stylesheet,
                'stylesheet': stylesheet,
            
            }
        
        return self.render_response('home.html',**context)
    
    def set_current_namespace(self, subdomain):
        namespace_manager.set_namespace(subdomain)
        logging.info(str(namespace_manager.get_namespace()))
     
class ProductHandler(BaseHandler):
    def get(self, product=None, category=None, subdomain=None):
        stylesheet = None   #Should be defined in shop model
        currency = 'GBP'    #Should be defined in shop model
        product_data = Product()
        images = []
        query = Image.gql("WHERE user = :1", subdomain)
        for image in query:
            if image.key().name()[0] == product_data.product_id:
                images.append(image)
        context = {
                   'shop_id'    :   product_data.shop_id,
                   'shop_name'  :   subdomain,    #Shop Name should be referenced from Shop ID
                   'id'         :   product_data.product_id,
                   'name'       :   product_data.name,
                   'description':   product_data.description,
                   'category_id':   product_data.category_id,
                   'category'   :   category,     #Category Name should be referenced from Category ID
                   'price'      :   product_data.price,
                   'images'     :   images,
                   'tags'       :   product_data.tags,
                   'quantity'   :   product_data.quantity,
                   'options'    :   product_data.options,
                   'currency'   :   currency,
                   'stylesheet' :   stylesheet
                    }
        self.render_response('product.html',**context)
 
class ImageUploadHandler(BaseHandler):
    def get(self, subdomain=None):
        upload_url = blobstore.create_upload_url('/upload')
        images = Image.gql("WHERE user = :1",subdomain)
        context = {
                   'images':        images,
                   'upload_url':   upload_url
                   }
        self.render_response('upload.html',**context)
                
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self,subdomain=None):
        product_id=self.request.get("product_id")
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]  
        for i in range(0,5):
            count = Image.gql("WHERE __key__=KEY('Image','%s-%s') LIMIT 1" % (product_id,i)).count()
            if count == 0:
                image = Image(blob_key=str(blob_info.key()),key_name='%s-%s' %(product_id, i),user=subdomain)
                image.put()
                self.redirect('/serve/%s' % blob_info.key())
                break;
        self.response.out.write('Maximum number of images for this product id, please delete one before uploading.'),
class ServeHandler(webapp2.RequestHandler):
    def get(self,resource,subdomain=None):
        logging.info('serve')
        self.response.out.write("%s %s" % (images.get_serving_url(resource, 100),
        images.get_serving_url(resource, 480)))
        
class DeleteImageHandler(webapp2.RequestHandler):
    def post(self, image_key=None, subdomain=None):
        image_key = self.request.get('image_key')
        image = Image.get_by_key_name(image_key)
        image.delete()
        self.redirect(webapp2.uri_for('imageupload'))