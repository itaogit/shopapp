'''
    ***
    Anything final yet
    ***

'''



from __future__ import division
import handlers
from google.appengine.ext import db
from tipfy.ext.wtforms import Form, fields
from tipfy import url_for,Response,render_json_response
from tipfy.ext.auth.model import UserData
from countries import countries,country_map
import pickle
import settings
import logging, datetime
from voucher import Voucher
from voucher import voucher_any_products
from dbmodels import GiftVoucher,Credit,PromoCodeUsage
import urllib
import simplejson



 
class BasketForm(Form):
    country  = fields.SelectField('Country', default='GB', choices=countries)
    voucher = fields.TextField('Promotional Code')
    gift_voucher_value = fields.TextField('Amount')
    options = fields.RadioField(u'Options', choices=[('None', 'None'),('All', 'All'), ('Part', 'Part')])
    page_lock = fields.BooleanField('Unlock Basket')
    
class Cart():
    '''Object that won't be persistent in the datastore'''
    def __init__(self):
        self.version = settings.CART_VERSION
        self.items = []
        self.promoitems = []
        self.country = 'GB'
        self.user_set_country = False
        self.sub_total_price = 0.0
        self.delivery = {'price':0.0, 'name':'none'}
        self.sub_total_vat = 0.0
        self.all_ok = True
        self.promo_applied = False
        """Aim to remove voucher reference"""
        self.voucher = None
        self.voucher_calc = False
        self.credit = 0.00
        self.credit_total_calced = 0.00
        self.deducted = False
        self.use_gift_voucher = False
        self.credit_used_calced = 0.00
        self.locked = False
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.original_value = 0.00
        

    def empty(self):
        self.__init__()
        
    def get_items_list(self):
        if self.promo_applied == True:
            return self.promoitems
        else:
            return self.items

    def item_in_cart(self,item):
        for i in self.items:
            if i.isbn == item:
                return True
        return False
    
    def how_many(self,item):
        for i in self.items:
            if i.isbn == item:
                return i.qty
        return 0
    
    def audio_download_in_cart(self,item):
        for i in self.items:
            if i.isbn == item and i.format == "Audio Download":
                return True
        return False
        
    @property
    def total(self):
        return len(self.items)
    
    @property
    def total_price(self):
        return self.delivery['price'] + self.sub_total_price
    
    @property
    def total_vat(self):
        if self.sub_total_vat == 0:
            return 0
        delprice = self.delivery['price']
        del_vat = 0
        if delprice:
            del_vat = delprice / (100+settings.VAT_RATE) * settings.VAT_RATE
            del_vat = round(del_vat, 2)
        return del_vat + self.sub_total_vat

    def set_country(self, country):
        self.country = country
        self.recalc()
        
    def search_for_item(self,isbn):
        item_to_change = None
        for item in self.items:
            if item.isbn == isbn:
                item_to_change = item
                break
        return item_to_change
        

    def add_gift_voucher(self,giftvoucher):
        self.items.append(giftvoucher)
        self.recalc()
        for i in self.items:
            logging.info(i.title)
        
    def add_item(self, doc):
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.voucher = None
        found = [i for i in self.items if i.isbn == doc['id']]
        if found and self.useonce_applied == False and self.voucher_total_bool == False:
            item = found[0]
            if item.format != "Audio Download" and int(item.qty) <= 10 and int(item.qty) > 0:
                item.qty += 1
        else:
            self.items.append(CartItem(doc))
        self.recalc()
    
    def change_item_qty(self, ref, qty):
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.voucher = None
        if self.useonce_applied == False:
            try:
                try:
                    num = int(qty)
                except:
                    num = 1
                item = self.items[ref]
                if item.format != "Audio Download" and item.format != "Voucher" and num > 0 and num <= 10:
                    item.qty = num 
                self.recalc()
            except:
                self.recalc()
                
    def change_item_qty_by_isbn(self, isbn, qty):
        self.voucher_total_bool = False
        self.voucher = None
        logging.info(str(self.useonce_applied))
        if self.useonce_applied == False:
            try:
                try:
                    num = int(qty)
                except:
                    num = 1
                for item in self.items:
                    if item.isbn == isbn:
                        item_to_change = item
                        logging.info(str(item_to_change))
                        break
                if item_to_change.format != "Audio Download" and item_to_change.format != "Voucher" and num > 0 and num <= 10:
                    logging.info(str(num))
                    item_to_change.qty = num
                self.recalc()
            except Exception,e:
                logging.info(e)
                self.recalc()            
        
    def remove_vat(self,ref):
        self.items[ref].vat = 0.00
        self.recalc()
        
    def change_item_price(self, ref, price):
        self.items[ref].price = price
        self.recalc()
     
    def remove_item(self, ref):
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.voucher = None
        del self.items[ref]
        self.recalc()
        
    def remove_item_by_isbn(self, isbn):
        self.useonce_applied = False
        self.voucher_total_bool = False
        self.voucher = None
        item_to_change = None
        for i in range(len(self.items)):
            item = self.items[i]
            if str(item.isbn) == str(isbn):
                item_to_change = i
                break
        if item_to_change != None:
            del self.items[item_to_change]
        self.recalc()

    def recalc(self):
        from territory import get_territory_info
        from vat import get_vat_info
        from delivery import get_delivery_info
        from countries import get_region
        if self.items:
            try:
                if self.voucher:
                    self.voucher_result = voucher_any_products(self,str(self.voucher))
                    if self.voucher_result == False:
                        self.voucher = None
            except:
                pass
            if self.useonce_applied == False and self.voucher_total_bool == False:
                items, self.all_ok = get_territory_info(self.items, self.country)
                items, self.sub_total_vat, self.sub_total_price = get_vat_info(self.items, get_region(self.country))
                try:
                    self.original_value = self.delivery['price'] + self.sub_total_price
                except:
                    self.original_value = 0.00
            try:
                dp = self.voucher_applied_shipping
            except:
                logging.info('getting shipping')
                self.delivery = get_delivery_info(self.items, get_region(self.country), self.country)
                if self.delivery['name'] == None or self.delivery['name'] == "":
                    self.delivery['name'] = "Download"
            if self.credit <= 0.00:
                self.credit_total_calced = 0.00
                self.credit_used_calced = 0.00
            if self.use_gift_voucher == True:
                logging.info('using gift voucher')
                try:
                    if self.voucher_total_bool == False and self.voucher:
                        self.credit_total = ((self.delivery['price'] + self.sub_total_price) - self.credit)
                    else:
                        self.credit_total = (self.total_price) - (self.credit)
                    logging.info('credit total ' + str(self.credit_total))
                    if self.credit_total >= 0.00:
                        self.credit_total_calced = self.credit_total
                        self.credit_used_calced = self.credit
                    elif self.credit_total < 0.00:
                        self.credit_total_calced = 0.00
                        self.credit_used_calced = (self.credit - (self.credit_total * -1.00))
                except Exception,e:
                    logging.info(e)
                    logging.info("problem with credit")

        else:
            self.empty()

    def contains(self,isbn_text):
        for i in self.items:
            for j in isbn_text:
                if i.isbn == j:
                    return True
        return False


class CartItem():
    def __init__(self, doc):
        self.qty = 1
        self.doc = doc

    @property
    def isbn(self):
        return self.doc['id']
    
    @property
    def ipnum(self):
        try:
            return self.doc['ipnum']
        except:
            return None

    @property
    def title(self):
        return self.doc['title']

    @property
    def format(self):
        return self.doc['format']

    @property
    def region(self):
        logging.info('REGION')
        logging.info(self.doc)
        try:
            if self.doc.has_key("release_country_s"):
                country = self.doc['release_country_s']
                if country == "UK":
                    country = "GB"
            else:
                country = "GB"
        except:
            country = "GB"
        return country

    @property
    def postage_adj_i(self):
        try:
            return self.doc['postage_adj_i']
        except:
            return None

    @property
    def tcode(self):
        try:
            return self.doc['territories']
        except:
            return '2'
    
    @property
    def release(self):
        try:
            return self.doc['release']
        except:
            return "1870-1-1"

    @property
    def vat(self):
        try:
            try:
                vp = self.voucher_vat
                return vp
            except:
                if self.doc['vat']:
                    the_vat = self.price / (100+settings.VAT_RATE) * settings.VAT_RATE
                    the_vat = round(the_vat, 2)
                    return the_vat 
                else:
                    return 0
        except:
            return 0

    @property
    def no_cd(self):
        try:
            return self.doc['no_cd']
        except:
            return 1
    
    @property
    def offer_price(self):
        try:
            return float(self.doc['offer_price'])
        except:
            return None

    @property
    def price(self):
        try:
            try:
                return self.voucher_price
            except:
                return self.doc['offer_price']
        except:
            try:
                return self.voucher_price
            except:
                return self.doc['price']


class CartViewerHandler(handlers.BaseHandler):
    def get(self):
        id = self.request.args.get('id', type=int)
        stored_cart = StoredCart().get_by_id(id)
        cart = stored_cart.get_cart()
        bform = BasketForm() 
        bform.country.data = cart.country
        context = {
           'image_linker' : handlers.image_linker,
           'cart' : cart,
           'form' : bform,
           'merchant_id': settings.MERCHANT_ID,
        }
        return self.render_response('cart.html', **context)

class CartHandler(handlers.BaseHandler):

    def get(self, minisite=None):
        cookie = self.get_secure_cookie('cart',max_age=2592000)
        cart = self.session.setdefault('cart', Cart())
        if len(cart.items) < 1:
            try:
                if self.auth_current_user == None or cookie['user'] == self.auth_current_user.username:
                    cart.useonce_applied = False
                    cart.voucher_total_bool = False
                    cart.voucher = None
                    for i in cookie['items']:
                        doc = get_item_data(i)
                        cart.add_item(doc)
                    cart.recalc()
            except:
                pass
                
        #doing this to clear out old cart type
        try :
            v = cart.version
            if v != settings.CART_VERSION:
                self.session.clear()
                cart = self.session.setdefault('cart', Cart())    
        except:
            self.session.clear()
            cart = self.session.setdefault('cart', Cart())
        cart.useonce_applied = False
        cart.voucher_total_bool = False
        cart.voucher = None
        cart.recalc()    
        empty = self.request.args.get('empty', None,)
        clear = self.request.args.get('clear', None,)
        to_add = self.request.args.get('add-product', None)
        to_remove = self.request.args.get('remove-product', None)
        #Checking for previous purchases if the user is logged in and has orders
        already_purchased = False
        user = self.auth_current_user
        try:
            already_purchased = check_if_brought(user,to_add)
            if already_purchased == True:
                self.set_message('error', 'You have already purchased this Audio Download', flash=True, life=10)
        except Exception, e:
                logging.error(e)
                pass
        if empty:
            cart.empty()
            cart.recalc()
        elif clear:
            self.session.clear()
        elif to_add and already_purchased == False:
            try:
                doc = get_item_data(to_add)
                if doc:
                    cart.add_item(doc)
                    cart = remove_voucher(cart)
            except:
                self.set_message('error', 'No item with this isbn can be found', flash=True, life=10)
                self.redirect("/cart")
        elif to_remove:
            try:
                cart.remove_item(int(to_remove))
                cart = remove_voucher(cart)
            except:
                self.set_message('error', 'Not a valid item.', flash=True, life=10)
                self.redirect("/cart")
        
        if not cart.user_set_country:
            # if cart.country not yet set by logged in user
            # get country from logged in user 
            # only done once until cart is emptied
            if self.auth_current_user:
                user = self.auth_current_user
                userdata = UserData.get_by_username(user.username)
                if userdata:
                    cart.set_country(userdata.country)
                else:
                    cart.set_country("UK")
                cart.user_set_country = True
           
        
        if cart.voucher:
                result = voucher_any_products(cart,str(cart.voucher))
                if result == True:
                    cart.recalc()
        try:
            locked = Credit.voucher_locked(self.session.sid,user)     
            if locked == True:
                cart.locked = True
                cart.credit = 0.00
                cart.deducted = False
            else:
                cart.locked = False
        except:
            pass
        used_other_promo_msg = False
        bform = BasketForm() 
        bform.country.data = cart.country
        self.session['cart'] = cart
        date = datetime.datetime.now()  
        items_list_cookie = []
        voucher_args = self.request.args.get('voucher',None)
        if voucher_args:
#            offers_used_already = False
#            for i in cart.items:
#                try:
#                    if i.offer_price > 0:
#                        offers_used_already = True
#                        break
#                except:
#                    pass
#            if offers_used_already == False:
            voucher_args = str(voucher_args).lower()
            cart.voucher = voucher_args
            cart.recalc()
#            else:
#                cart.voucher = None
#                used_other_promo_msg = True
#                self.set_message('error', 'This code cannot be used in conjunction with any other offer.', flash=True, life=10)
#                return self.get(**kwargs)
        else:
            if not cart.voucher:
                cart.useonce_applied = False
                cart.voucher_total_bool = False
                cart.voucher = None
                cart.recalc()    
        for i in cart.items:
            for j in range(i.qty):
                items_list_cookie.append(i.isbn)
                
        cookie['items'] = items_list_cookie
        cookie['total'] = cart.total
        cookie['total_price'] = cart.total_price
        if self.auth_current_user:
            cookie['user'] = user.username
        else:
            cookie['user'] = 'None'
        cookie_value = cookie.serialize()
        hamleys=False
        if minisite=='hamleys':
            hamleys=True
        context = {
           'image_linker' : handlers.image_linker,
           'cart' : cart,
           'form' : bform,
           'merchant_id': settings.MERCHANT_ID,
            'convertdate':handlers.unicode_to_date,
            'date':date,
            'used_other_promo_msg':used_other_promo_msg,
            'hamleys': hamleys
        }
        cart_check = self.session.get('cart',None)
        if cart_check:
            opts = {
                    'country':str(cart.country)
                    }
        else:
            opts = {'id': self.session.sid,
                    'country':str(cart.country)}
        self.request.context.update( {
            'sagepaycheckout':   url_for('scheckout', **opts),
            })
        if self.auth_current_user:
            if hamleys == True:
                return self.redirect('/hamleys/checkout')
            return self.redirect('/checkout')
        else:
            return self.render_response('cart.html', **context)

    def post(self, **kwargs):
        logging.info('cart update')
        cart = self.session.get('cart',None)
        if cart:
            all_list = self.request.form.getlist('allitems[]')
            qtyupdate = self.request.form.getlist('qty[]')
            
            if all_list:
                for i in range(len(all_list)):
                    cart.change_item_qty(i, qtyupdate[i])
            self.session['cart'] = cart
            return self.redirect('/cart')
    
class CartService(handlers.BaseHandler):
    def head(self):
        return Response('')
    def get(self,**kwargs):
        return self.redirect('/cart')
    def post(self):
        status = None
        cart = self.session.get('cart',None)
        if cart:
            """GET country GET Argument"""
            country = self.request.form.get('country',None)
            logging.info("COUNTRY " + country)
            """Take first four characaters, should only require two. Limits possible attacks on code below """
            if country:
                country = country[0:4]
            """Check valid country"""
            if country_map.has_key(str(country)):
                """set the cart country as the new country"""
                cart.set_country(country)
                cart.user_set_country = True
                status = "OK"
            '''Update Item Totals'''
            all_list = self.request.form.getlist('allitems[]')
            qtyupdate = self.request.form.getlist('qty[]')    
            if all_list:
                for i in range(len(all_list)):
                    cart.change_item_qty(i, qtyupdate[i])    
        else:
            status = "COUNTRY_FAIL"
        logging.info("CART TOTAL " + str(cart.total_price))
        self.session['cart'] = cart
        context = {'status':status,
                   'delivery': (cart.delivery),
                   'cart_total_price':cart.total_price,
                   'cart_total_vat':cart.total_vat
                   }
        if self.request.is_xhr:
            return render_json_response(context)
        else:
            return self.redirect('/cart')
    
    
def valid_voucher_user_check(user,voucher):
    try:
        voucher_try = Voucher().get_by_code(str(voucher))
        for i in voucher_try.email:
            if voucher_try.email[0] == '':
                return 0
    except:
        return 1
    if user:
        for email in voucher_try.email:
            if str(user.username) == str(email):
                return 2
    return 3
    
def item_brought_check(user, voucher,cart):
    already_purchased = False
    try:
        voucher_try = Voucher().get_by_code(str(voucher))
    except:
        return False
    try:
        if user and voucher_try != None:
            for to_add in voucher_try.isbn:
                already_purchased = check_if_brought(user,to_add)
                if already_purchased == False:
#                    doc = get_item_data(str(to_add))
#                    cart.add_item(doc)
                    return False
                elif already_purchased == True:
                    cart.voucher = None
                    logging.info('2')
                    return True                
        elif voucher_try != None:
            for i in voucher_try.isbn:
                to_add = str(i)
#                doc = get_item_data(to_add)
#                cart.add_item(doc)
                return False
        else:
            return False
    except:
        return False
    
def check_valid_voucher(voucher):
    try:
        voucher_try = Voucher().get_by_code(str(voucher))
        check = str(voucher_try.voucher_id)
        return True
    except:
        return False
        
def check_for_gift_voucher(voucher_no, user):
    try:
        if voucher_no != "" and len(voucher_no) != 16:
            current_voucher = GiftVoucher().get_by_voucher_no(str(voucher_no))
            try:
                email = current_voucher.to_email
                return True
            except:
                return False
        elif len(voucher_no) == 16:
            promocode = Voucher().get_by_code(voucher_no)
            if promocode and PromoCodeUsage().check_by_code(voucher_no):
                promocode_status = "This voucher has already been used."
                return False
            elif promocode and promocode.expiry < datetime.date.today():
                promocode_status = "This voucher has expired."
                return False
            elif promocode:
                
                PromoCodeUsage().create(voucher_no,user)
                """CREATE GIFT VOUCHER"""
                logging.info("CHECKING OUT YEAH")
                #Credit.create_or_add(user, promocode.percentage, 0.0,'')
                return True
                
            else:
                return False
        else:
            return False
    except:
            return False
    
"""def check_if_brought(user,to_add):
    already_purchased= False
    try:
        if user and user.orders:
            for i in user.orders:
                try:
                    stored_cart_data = StoredCart().get(i.cart_key)
                    cart_data = stored_cart_data.get_cart()
                    for j in cart_data.items:
                        if j.isbn == to_add and j.format == "Audio Download" and already_purchased == False:
                            return True
                except:
                    return False
                
    except Exception,e:
        logging.info(e)
        return False
        
    return already_purchased"""
    
def check_if_brought(user,to_add):
    already_purchased= False
    try:
        if user and user.downloads:
            for i in user.downloads:
                if i.isbn == to_add and already_purchased == False:
                    return True
            return False
    except Exception,e:
        logging.info(e)
        return False
        
    return already_purchased

def get_item_data(isbn):
    try:
        logging.info('item data ' + str(isbn))
    except:
        pass
    import urllib2
    import simplejson
    list = []
    field_list = 'ipnum,id,format,title,price,vat,offer_price,no_cd,territories,release_country_s,release,postage_adj_i'
    solr_query = '%swt=json&json.nl=arrarr&fl=%s&q=id:%s' % (settings.ADMIN_SOLR, field_list, isbn)
    conn = urllib2.urlopen(solr_query)
    rsp = simplejson.load(conn)
    try:
        item_data = rsp['response']['docs'][0]
    except:
        item_data = None
    return item_data

def remove_voucher(cart):
    cart_new = Cart()
    n = 0
    for i in cart.items:
        if str(i.format) != "Voucher":
            doc = get_item_data(i.isbn)
            if doc:
                cart_new.add_item(doc)
                cart_new.change_item_qty(n, i.qty)
                n = n +1
        elif str(i.format) == "Voucher":
            cart_new.add_gift_voucher(i)
    cart_new.country = cart.country
    cart_new.user_set_country = cart.user_set_country
    cart_new.credit = cart.credit
    cart_new.deducted = cart.deducted
    cart_new.useonce_applied = False
    cart_new.voucher_total_bool = False
    cart_new.voucher = ""
    cart_new.original_value = cart.total_price
    cart.empty()
    return cart_new
        
if __name__ == '__main__':
    cart = Cart()
    doc = get_item_data('9781846071171')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    doc = get_item_data('9781408466674')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    doc = get_item_data('9781408467152')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.remove_item(1)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.change_item_qty(1, 3)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.set_country('US')
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    for i in cart.items:
        print i.isbn, i.tcode, i.ok_to_buy, i.price
    cart.empty()
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok

    doc = get_item_data('9781846071171')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    doc = get_item_data('9781408466674')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    doc = get_item_data('9781408467152')
    cart.add_item(doc)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.remove_item(1)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.remove_item(1)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok
    cart.remove_item(0)
    print cart.total, cart.total_price, cart.delivery, cart.total_vat, cart.all_ok

