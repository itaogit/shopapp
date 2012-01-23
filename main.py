import settings
import webapp2
import handlers
from webapp2_extras import routes

''''''



app = webapp2.WSGIApplication([
    #Main site
    routes.DomainRoute( settings.DOMAIN, [webapp2.Route('/', handler='handlers.PageHandler'),
                                                           webapp2.Route('/<category>/<product>',handler='handlers.ProductHandler')]),
    #Subsites
    routes.DomainRoute(r'<subdomain:(?!www\.)[^.]+>.<:.*>', [webapp2.Route('/', handler='handlers.SiteHandler'),
                                                             webapp2.Route('/<category>/<product>',handler='handlers.ProductHandler')]),
    webapp2.Route(r'/', handler='handlers.PageHandler'),
    webapp2.Route(r'/([^/]+)', 'handlers.PageHandler'),
])



def main():
  run_wsgi_app(app)


if __name__ == '__main__':
  main()