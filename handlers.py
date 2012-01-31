'''Import section'''
import webapp2
import main
import logging
from webapp2_extras import jinja2, sessions
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import images
from models import Shop, Product, Image, Item, Category
from google.appengine.api import namespace_manager
from google.appengine.api import memcache
from google.appengine.ext import db
'''End import section'''

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)
    
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            
            self.session_store.save_sessions(self.response)
            
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
    
    
    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

class PageHandler(BaseHandler):
    def get(self, page='home'):
        self.session()
        
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
            
class CreateCatHandler(BaseHandler):
    def get(self, subdomain):       
        namespace_manager.set_namespace(subdomain)
        entity = Category(key_name='New Category', categoryname='New Category')
        entity.put()
        self.response.write('Category created')           

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
        shop_data = Shop(shopname='Shop Name',
                         description='Shop description',
                         )
        product1 = Product(name='Product1',category='category1',images = [db.BlobKey('AMIfv96K-UYNqA3YFFIEfCGZtf-R7id0JdL6vjxeuIOf_htLh7ojjdsR0SMTRFIYL2Ax8ciV0bxAFd7oOC5xkqh4gGq6qGFZQ2cU3_7x3GVwgz_IumGDNoGrEtxX5YNCszudH8Re67o6oK5_T-aL0g9PVUs4aCtyPw')])
        product2 = Product(name='Product2',category='category2',images = [db.BlobKey('AMIfv96TUHz2REWJf__9p0D3aWSfQUVdJRaD7GjLKiQXeeC5iGVhNtRoo0RZ4Ez_o6EW-zeEyanj6WyUXfrLOQ2TbxxKQlR-u3Omb67M8ljAEzdtw5EgpL6NZ9jotWfMi0Vk3Q5vMLH33vWc-NCS34C5YoMAwVfGlw')])
        product3 = Product(name='Product3',category='category3',images = [db.BlobKey('AMIfv94jnaylMAKY3p9r3M-MrUvePQP4zmvb9OWAruqYerm2K4M4MWK1rxl-yUXcBPbzZyr_ZnxwrF66cDg-FeJgvFVLu4UkVDA5uY0A3bO72jXxOkSk6B7zyelW80RDZkt85pbQVvzTKctfLHzXmtgJCnan7PTvnw')])
        product4 = Product(name='Product4',category='category4',images = [db.BlobKey('AMIfv976U_t-de4wQDlyf_nRlNzqne1PvHfXYnLPuL6W5Lmac1BRbRfDdaT8_PtRSYhTU8-r5deBRRygNLnGLac8cd0vtWFgKCrog0D2bcuZrWkE1kj74JkEoOqb6mRMxfpnz3ZCKJSSqn91xanIh2XTDrAoerE0-g')])
        product5 = Product(name='Product5',category='category5',images = [db.BlobKey('AMIfv94DSiOdBxqxXLLYFxvDjM_SGYtChAIG4GZj_KTgtkDkDyoktnZzaiwp38VmpAeyGZkMBxroM3INcVu5fA125befbbUgcPfCaeyPxvtwIDgVw7cSvIjm0Bu1W3z9LJEY0kC0BIBpdbdfQ32LFFKwqC3esPei4g')])
        product6 = Product(name='Product6',category='category6',images = [db.BlobKey('AMIfv96K-UYNqA3YFFIEfCGZtf-R7id0JdL6vjxeuIOf_htLh7ojjdsR0SMTRFIYL2Ax8ciV0bxAFd7oOC5xkqh4gGq6qGFZQ2cU3_7x3GVwgz_IumGDNoGrEtxX5YNCszudH8Re67o6oK5_T-aL0g9PVUs4aCtyPw')])
        product7 = Product(name='Product7',category='category7',images = [db.BlobKey('AMIfv96TUHz2REWJf__9p0D3aWSfQUVdJRaD7GjLKiQXeeC5iGVhNtRoo0RZ4Ez_o6EW-zeEyanj6WyUXfrLOQ2TbxxKQlR-u3Omb67M8ljAEzdtw5EgpL6NZ9jotWfMi0Vk3Q5vMLH33vWc-NCS34C5YoMAwVfGlw')])
        product8 = Product(name='Product8',category='category8',images = [db.BlobKey('AMIfv94jnaylMAKY3p9r3M-MrUvePQP4zmvb9OWAruqYerm2K4M4MWK1rxl-yUXcBPbzZyr_ZnxwrF66cDg-FeJgvFVLu4UkVDA5uY0A3bO72jXxOkSk6B7zyelW80RDZkt85pbQVvzTKctfLHzXmtgJCnan7PTvnw')])
        product9 = Product(name='Product9',category='category9',images = [db.BlobKey('AMIfv976U_t-de4wQDlyf_nRlNzqne1PvHfXYnLPuL6W5Lmac1BRbRfDdaT8_PtRSYhTU8-r5deBRRygNLnGLac8cd0vtWFgKCrog0D2bcuZrWkE1kj74JkEoOqb6mRMxfpnz3ZCKJSSqn91xanIh2XTDrAoerE0-g')])
        product10 = Product(name='Product10',category='category1',images = [db.BlobKey('AMIfv94DSiOdBxqxXLLYFxvDjM_SGYtChAIG4GZj_KTgtkDkDyoktnZzaiwp38VmpAeyGZkMBxroM3INcVu5fA125befbbUgcPfCaeyPxvtwIDgVw7cSvIjm0Bu1W3z9LJEY0kC0BIBpdbdfQ32LFFKwqC3esPei4g')])
        product11 = Product(name='Product11',category='category1',images = [db.BlobKey('AMIfv96K-UYNqA3YFFIEfCGZtf-R7id0JdL6vjxeuIOf_htLh7ojjdsR0SMTRFIYL2Ax8ciV0bxAFd7oOC5xkqh4gGq6qGFZQ2cU3_7x3GVwgz_IumGDNoGrEtxX5YNCszudH8Re67o6oK5_T-aL0g9PVUs4aCtyPw')])
        product12 = Product(name='Product12',category='category1',images = [db.BlobKey('AMIfv96TUHz2REWJf__9p0D3aWSfQUVdJRaD7GjLKiQXeeC5iGVhNtRoo0RZ4Ez_o6EW-zeEyanj6WyUXfrLOQ2TbxxKQlR-u3Omb67M8ljAEzdtw5EgpL6NZ9jotWfMi0Vk3Q5vMLH33vWc-NCS34C5YoMAwVfGlw')])
        product_data = [product1,product2,product3,product4,
                        product5,product6,product7,product8,
                        product9,product10,product11,product12,]
        categories = []
        for product in product_data:
            if product.category not in categories:
                categories.append(product.category)
        context = {
                'title': subdomain,
                'pagecontent': 'this is the ' + subdomain + ' page',
                #'stylesheet': site.stylesheet,
                'stylesheet': stylesheet,
                'shop_name':    shop_data.shopname,
                'shop_description': shop_data.description,
                'categories':   categories,
                'products': product_data,
                'cart_total':0,
                'page':1,
                'pages':6,
                'currency': 'GBP',
                'imagelinker':   image_linker,
                #######    dummy data    #######
            }
        
        return self.render_response('home.html',**context)
    
    def set_current_namespace(self, subdomain):
        namespace_manager.set_namespace(subdomain)
        logging.info(str(namespace_manager.get_namespace()))
     
class ProductHandler(BaseHandler):
    def get(self, product=None, category=None, subdomain=None):
        stylesheet = None   #Should be defined in shop model
        currency = 'GBP'    #Should be defined in shop model
        product_data = Product(stock = 10,
                               description = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras imperdiet enim ac augue auctor viverra. Phasellus congue tempor justo sed cursus. Quisque non quam turpis. Curabitur mollis luctus tempor. Aliquam sit amet nisl vel arcu rutrum ornare at vel sem.',
                               name = 'Product',
                               price = 10.00,
                               tags = ['keyword1','keyword2','keyword3','keyword4'],
                               images = [db.BlobKey('AMIfv96K-UYNqA3YFFIEfCGZtf-R7id0JdL6vjxeuIOf_htLh7ojjdsR0SMTRFIYL2Ax8ciV0bxAFd7oOC5xkqh4gGq6qGFZQ2cU3_7x3GVwgz_IumGDNoGrEtxX5YNCszudH8Re67o6oK5_T-aL0g9PVUs4aCtyPw'),
                                         db.BlobKey('AMIfv96TUHz2REWJf__9p0D3aWSfQUVdJRaD7GjLKiQXeeC5iGVhNtRoo0RZ4Ez_o6EW-zeEyanj6WyUXfrLOQ2TbxxKQlR-u3Omb67M8ljAEzdtw5EgpL6NZ9jotWfMi0Vk3Q5vMLH33vWc-NCS34C5YoMAwVfGlw'),
                                         db.BlobKey('AMIfv94jnaylMAKY3p9r3M-MrUvePQP4zmvb9OWAruqYerm2K4M4MWK1rxl-yUXcBPbzZyr_ZnxwrF66cDg-FeJgvFVLu4UkVDA5uY0A3bO72jXxOkSk6B7zyelW80RDZkt85pbQVvzTKctfLHzXmtgJCnan7PTvnw'),
                                         db.BlobKey('AMIfv976U_t-de4wQDlyf_nRlNzqne1PvHfXYnLPuL6W5Lmac1BRbRfDdaT8_PtRSYhTU8-r5deBRRygNLnGLac8cd0vtWFgKCrog0D2bcuZrWkE1kj74JkEoOqb6mRMxfpnz3ZCKJSSqn91xanIh2XTDrAoerE0-g'),
                                         db.BlobKey('AMIfv94DSiOdBxqxXLLYFxvDjM_SGYtChAIG4GZj_KTgtkDkDyoktnZzaiwp38VmpAeyGZkMBxroM3INcVu5fA125befbbUgcPfCaeyPxvtwIDgVw7cSvIjm0Bu1W3z9LJEY0kC0BIBpdbdfQ32LFFKwqC3esPei4g'),
                                         db.BlobKey('AMIfv96K-UYNqA3YFFIEfCGZtf-R7id0JdL6vjxeuIOf_htLh7ojjdsR0SMTRFIYL2Ax8ciV0bxAFd7oOC5xkqh4gGq6qGFZQ2cU3_7x3GVwgz_IumGDNoGrEtxX5YNCszudH8Re67o6oK5_T-aL0g9PVUs4aCtyPw'),
                                         db.BlobKey('AMIfv96TUHz2REWJf__9p0D3aWSfQUVdJRaD7GjLKiQXeeC5iGVhNtRoo0RZ4Ez_o6EW-zeEyanj6WyUXfrLOQ2TbxxKQlR-u3Omb67M8ljAEzdtw5EgpL6NZ9jotWfMi0Vk3Q5vMLH33vWc-NCS34C5YoMAwVfGlw'),
                                         db.BlobKey('AMIfv94jnaylMAKY3p9r3M-MrUvePQP4zmvb9OWAruqYerm2K4M4MWK1rxl-yUXcBPbzZyr_ZnxwrF66cDg-FeJgvFVLu4UkVDA5uY0A3bO72jXxOkSk6B7zyelW80RDZkt85pbQVvzTKctfLHzXmtgJCnan7PTvnw'),
                                         db.BlobKey('AMIfv976U_t-de4wQDlyf_nRlNzqne1PvHfXYnLPuL6W5Lmac1BRbRfDdaT8_PtRSYhTU8-r5deBRRygNLnGLac8cd0vtWFgKCrog0D2bcuZrWkE1kj74JkEoOqb6mRMxfpnz3ZCKJSSqn91xanIh2XTDrAoerE0-g'),
                                         ],
                               visible = True
                               )
        product_data.set_options([{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']}])
        logging.info(product_data.get_options())
        context = {
                   'shop_id'    :   product_data.shop_id,
                   'shop_name'  :   subdomain,    #Shop Name should be referenced from Shop ID
                   'name'       :   product_data.name,
                   'description':   product_data.description,
                   'category'   :   category,     #Category Name should be referenced from Category ID
                   'price'      :   product_data.price,
                   'images'     :   product_data.images,
                   'tags'       :   product_data.tags,
                   'quantity'   :   product_data.stock,
                   'options'    :   product_data.get_options(),
                   'currency'   :   currency,
                   'stylesheet' :   stylesheet,
                   'imagelinker':   image_linker
                    }
        self.render_response('product.html',**context)
 
class ImageUploadHandler(BaseHandler):
    def get(self, subdomain=None):
        upload_url = blobstore.create_upload_url('/upload')
        images = ['1-1','1-2']
        context = {
                   'images':        images,
                   'upload_url':   upload_url,
                   'imagelinker':   image_linker
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
                self.redirect('/serve/%s-%s' % (product_id,i))
                break;
        self.response.out.write('Maximum number of images for this product id, please delete one before uploading.'),

class ServeHandler(webapp2.RequestHandler):
    def get(self,resource,subdomain=None):
        size = self.request.get("size",480)
        self.response.out.write(image_linker(resource,size))

def image_linker(resource,size=480, subdomain=None):
            return images.get_serving_url(resource, int(size))
        
class DeleteImageHandler(webapp2.RequestHandler):
    def post(self, image_key=None, subdomain=None):
        image_key = self.request.get('image_key')
        image = Image.get_by_key_name(image_key)
        image.delete()
        self.redirect(webapp2.uri_for('imageupload'))