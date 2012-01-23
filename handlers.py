import webapp2
import main
import logging
from models import Product
from webapp2_extras import jinja2
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

class SiteHandler(BaseHandler):
  def get(self, subdomain):
    #site_name = SUBDOMAIN_RE.search(self.request.host).group(1)
    import logging
    context = {}
    logging.info('SiteHandler')
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
    



     
class ProductHandler(BaseHandler):
    def get(self, product=None, category=None, subdomain=None):
        stylesheet = None   #Should be defined in shop model
        currency = 'GBP'    #Should be defined in shop model
        product_data = Product()
        context = {
                   'shop_id'    :   product_data.shop_id,
                   'shop_name'  :   subdomain,    #Shop Name should be referenced from Shop ID
                   'id'         :   product_data.product_id,
                   'name'       :   product_data.name,
                   'description':   product_data.description,
                   'category_id':   product_data.category_id,
                   'category'   :   category,     #Category Name should be referenced from Category ID
                   'price'      :   product_data.price,
                   'images'     :   product_data.images,
                   'tags'       :   product_data.tags,
                   'quantity'   :   product_data.quantity,
                   'options'    :   product_data.options,
                   'currency'   :   currency,
                   'stylesheet' :   stylesheet
                    }
        self.render_response('product.html',**context)