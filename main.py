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
                                                             webapp2.Route('/create',handler='handlers.CreateShopHandler'),
                                                             webapp2.Route('/add/<item>/<qty>',handler='handlers.AddItemHandler'),
                                                             webapp2.Route('/shoppingarea/<to_cache>',handler='handlers.ShoppingAreaHandler'),
                                                             webapp2.Route('/<category>/<product>',handler='handlers.ProductHandler'),
                                                             ]),
    webapp2.Route(r'/', handler='handlers.PageHandler'),
                        
    
    #webapp2.Route('/<category>/<product>', handler='handlers.ProductHandler', name='product'),
    webapp2.Route(r'/([^/]+)', 'handlers.PageHandler'),
])



def main():
  run_wsgi_app(app)


if __name__ == '__main__':
  main()