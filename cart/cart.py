from coupon.models import Coupon
from decimal import Decimal
from django.conf import settings
from shop.models import Product



class Cart(object):

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_ID)
        if not cart:
            cart = self.session[settings.CART_ID] = {}

        #현재 cart는 세션에서 가져오던지 settings에서 만들어진 cart이다.
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')


    def __len__(self):
        #cart에 제품들을 for문을 통해 
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

            yield item
    
    def add(self, product, quantity=1, is_update=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':0, 'price':str(product.price)}

        if is_update:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session[settings.CART_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del(self.cart[product_id])
            self.save()

    def clear(self):
        self.session[settings.CART_ID] = {}
        self.session['coupon_id'] = None
        self.session.modified = True

    def get_product_total(self,call='test'):
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())

    # 메서드가 아니라 attribute 처럼 동작시킴
    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    # 0원에서 discount 방지등의 계산을 하기위해
    def get_discount_total(self):
        if self.coupon:
            if self.get_product_total() >= self.coupon.amount:
                return self.coupon.amount
        return Decimal(0)

    def get_total_price(self):
        # 추후 배송비 등 부가세를 포함한 계산으로 확장될 수 있음 
        return self.get_product_total() - self.get_discount_total()
    