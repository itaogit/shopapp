'''Import section'''
import webapp2
import main
import logging
from models import Shop, Item
from webapp2_extras import jinja2
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
        logging.info('ProductHandler')
        if subdomain:
            stylesheet = 'bootstrap-' + subdomain + '.min.css'
        else:
            stylesheet = None
        context = {
                   'shop_name': 'Shop Name',
                   'id':             '1',
                   'name':           product,
                   'description':    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras imperdiet enim ac augue auctor viverra. Phasellus congue tempor justo sed cursus. Quisque non quam turpis. Curabitur mollis luctus tempor. Aliquam sit amet nisl vel arcu rutrum ornare at vel sem.',
                   'category':       category,
                   'price':          '%.2f' % 10.00,
                   'images':         [('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif')],
                   'tags':           ['keyword1','keyword2','Keyword3', 'keyword4'],
                   'quantity':       3,
                   'options':        [{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']}],
                   'currency':      'GBP',
                   'stylesheet':    stylesheet,
                    }
        self.render_response('product.html',**context)