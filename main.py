import settings
import webapp2
import handlers
from webapp2_extras import routes


''''''
config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'g04way'}


app = webapp2.WSGIApplication([
    #Main site
    routes.DomainRoute( settings.DOMAIN, [webapp2.Route('/', handler='handlers.PageHandler'),

                                          ]),

    #Subsites
    routes.DomainRoute(r'<subdomain:(?!www\.)[^.]+>.<:.*>', [webapp2.Route('/', handler='handlers.SiteHandler'),
                                                             
                                                             webapp2.Route('/admin',handler='checkout.RemoveFromCartHandler'),
                                                             webapp2.Route('/admin/login', handler='admin.LoginHandler',name='loginadmin'),
                                                             webapp2.Route('/admin/change-style', handler='admin.ChangeStyleHandler',name='loginadmin'),
                                                             webapp2.Route('/admin/products',handler='admin.ProductHandler', name="addproducts"),
                                                             webapp2.Route('/imageupload', handler='handlers.ImageUploadHandler', name='imageupload'),
                                                             webapp2.Route('/search', handler='search.SearchHandler', name='search'),
                                                             webapp2.Route('/delete', handler='handlers.DeleteImageHandler', name='del'),
                                                             webapp2.Route(r'/upload', handler='handlers.UploadHandler', name='upload'),
                                                             webapp2.Route(r'/serve/<resource>', handler='handlers.ServeHandler', name='serve'),
                                                             webapp2.Route('/<category>/<product>',handler='handlers.ProductHandler'),
                                                             webapp2.Route('/create',handler='handlers.CreateShopHandler'),
                                                             webapp2.Route('/createcat',handler='handlers.CreateCatHandler'),
                                                             webapp2.Route('/add/<item>/<qty>',handler='handlers.AddProductHandler'),
                                            
                                                             webapp2.Route('/shoppingarea/<to_cache>',handler='handlers.ShoppingAreaHandler'),
                                                             webapp2.Route('/<category>/<product>',handler='handlers.ProductHandler'),
                                                             webapp2.Route('/add-to-cart',handler='checkout.AddToCartHandler'),
                                                             webapp2.Route('/remove-from-cart',handler='checkout.RemoveFromCartHandler'),
                                                             
                                                             ]),

    #Testing
    routes.PathPrefixRoute(r'/test', [webapp2.Route('/', handler='tests.MainTest', name='test-overview'),
                                       
                                       ]),

                        
    
    #Localhost
    webapp2.Route(r'/', 'handlers.PageHandler'),
    webapp2.Route(r'/create_styles', 'handlers.CreateStyle'),
    webapp2.Route(r'/([^/]+)', 'handlers.PageHandler'),
],config=config)


def main():
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
