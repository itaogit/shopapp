class Product(db.Model):
    shop_id         = '1'
    category_id     = '1'
    product_id      = '1'
    name            = 'Test Product'
    description     = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras imperdiet enim ac augue auctor viverra. Phasellus congue tempor justo sed cursus. Quisque non quam turpis. Curabitur mollis luctus tempor. Aliquam sit amet nisl vel arcu rutrum ornare at vel sem.'
    price           = '%.2f' % 10.00
    images          = [('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif'),('http://placehold.it/480x360.gif','http://placehold.it/100x100.gif')]
    tags            = ['keyword1','keyword2','Keyword3', 'keyword4']
    quantity        =  3
    options         = [{'Size':['Large','Medium','Small']},{'Colour':['Red','White','Blue']}]
    
    
    