import webapp2

app = webapp2.WSGIApplication([
    (r'/', 'handlers.PageHandler'),
    webapp2.Route('/<category>/<product>', handler='handlers.ProductHandler', name='product'),
    (r'/([^/]+)', 'handlers.PageHandler'),
])
