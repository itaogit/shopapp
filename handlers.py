import webapp2
import main
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
            'pagecontent': 'this is the ' + page + ' page',
        }
        path = page + '.html'
        self.render_response(path, **context)
        
class ProductHandler(BaseHandler):
    def get(self, product=None, category=None):
        context = {
                   'shop_name': 'Shop Name',
                   'id':             '1',
                   'name':           product,
                   'description':    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras imperdiet enim ac augue auctor viverra. Phasellus congue tempor justo sed cursus. Quisque non quam turpis. Curabitur mollis luctus tempor. Aliquam sit amet nisl vel arcu rutrum ornare at vel sem.',
                   'category':       category,
                   'price':          '%.2f' % 10.00,
                   'images':         [('http://placehold.it/480x360','http://placehold.it/100x100'),('http://placehold.it/480x360','http://placehold.it/100x100'),('http://placehold.it/480x360','http://placehold.it/100x100'),('http://placehold.it/480x360','http://placehold.it/100x100'),('http://placehold.it/480x360','http://placehold.it/100x100')],
                   'tags':           ['keyword1','keyword2','Keyword3', 'keyword4'],
                   'quantity':       3,
                   'options':        [{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']}],
                   'currency':      'GBP'
                    }
        self.render_response('product.html',**context)