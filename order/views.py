from cart.cart import Cart
from django.shortcuts import render, get_object_or_404
from order.models import *
from order.forms import *


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                # order.discount = cart.coupon.amount
                # 할인에 대한 계산을 한 후에 그 금액값을 가져옴
                order.discount = cart.get_discount_total()
                order.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            return render(request, 'order/created.html', {'order':order})
    else:
        form = OrderCreateForm()
    return render(request, 'order/create.html', {'cart':cart, 'form':form})