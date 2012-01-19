import webapp2
import os
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

app = webapp2.WSGIApplication([
    (r'/', PageHandler),
    (r'/([^/]+)', PageHandler),
])
