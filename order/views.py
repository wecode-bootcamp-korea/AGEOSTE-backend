import json

from django.views import View
from django.http  import JsonResponse

from .models     import Cart
from user.utils  import check_user
from user.models import User, UserCoupon, Coupon


class PaymentView(View):
    @check_user
    def patch(self, request):
        data          = json.loads(request.body)
        user          = request.user
        user_address  = user.address
        order_address = data.get('address')

        if user_address is None:
            User.objects.filter(id=user.id).update(address=order_address)
            return JsonResponse({"message": "SUCCESS"}, status=200)


    @check_user
    def get(self, request):
        try:
            user    = request.user
            carts   = Cart.objects.filter(user=user).select_related('product', 'user', 'size', 'color')
            coupons = UserCoupon.objects.filter(user=user).select_related('user', 'coupon')

            carts_list = [{
                "product"       : cart.product.name,
                "discount_rate" : cart.product.discount_rate,
                "size"          : cart.size.name,
                "color"         : cart.color.name,
                "thumbnail"     : cart.thumbnail.image_url,
                "quantity"      : cart.quantity
            } for cart in carts]

            coupons_list = [{
                "coupon"               : coupon.coupon.name,
                "coupon_discount_rate" : coupon.coupon.discount_rate
            } for coupon in coupons]

            membership = {
                "grade"         : user.membership.grade,
                "discount_rate" : user.membership.discount_rate
            }

            return JsonResponse({"carts_list" : carts_list, "coupons_list" : coupons_list, "membership" : membership}, status=200)

        except CartDoesNotExist:
            return JsonResponse({"error": "INVALID_CART"}, status=400)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)
