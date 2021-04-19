from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import AddCouponForm


@require_POST
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']

        try:
            # usefrom(사용할수 있는 시간이 현재시점 보다 작고) use_to (사용만료시간이 현재시점보다 커야함)
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now, use_to__gte=now, active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    return redirect('cart:detail')