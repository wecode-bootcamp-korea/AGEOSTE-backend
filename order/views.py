import json

from django.views     import View
from django.http      import JsonResponse

from .models          import Cart
from product.models   import Product, Color, Size, Image
from user.models      import User, UserCoupon, Coupon
from user.utils       import check_user


class CartView(View):
    @check_user
    def get(self, request):
        carts = request.user.carts.select_related("product", "size", "color", "thumbnail")

        cart_list = [{
            "name"          : cart.product.name,
            "price"         : cart.product.price,
            "discount_rate" : cart.product.discount_rate,
            "thumbnail"     : cart.thumbnail.image_url,
            "size"          : cart.size.name,
            "color"         : cart.color.name,
            "count"         : cart.quantity,
        }for cart in carts]

        return JsonResponse({'CART_LIST' : cart_list},status=200)

    @check_user
    def post(self, request):
        try:
            data    = json.loads(request.body)
            cart, _ = Cart.objects.get_or_create(
                user         = request.user,
                product_id   = data['product_id'], 
                size_id      = data['size_id'],
                color_id     = data['color_id'],
                thumbnail_id = data['image_id'],
            )

            cart.quantity +=1
            cart.save()

            return JsonResponse({"MESSAGE" : "Create Cart"}, status=201)

        except Size.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Size does not exist"}, status=400)

        except Color.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Color does not exist"}, status=400)

        except Image.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Image does not exist"}, status=400)

        except Product.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Product does not exist"}, status=400)

        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status=400)

    @check_user
    def put(self, request):
        try:
            data       = json.loads(request.body)
            cart       = Cart.objects.get(user = request.user, id = data['cart_id'])
            cart.count = data['count']
            cart.save()

            return JsonResponse({'MESSAGE' : '카트의 수량을 수정했습니다.'}, status=200)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Cart does not exist"}, status=400)

        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status=400)

    @check_user
    def delete(self, request):
        try:
            data = json.loads(request.body)
            Cart.objects.get(user = request.user, id = data['cart_id']).delete()
            return JsonResponse({"MESSAGE" : "Delete cart"}, status=200)

        except Cart.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Cart does not exist"}, status=400)

        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status=400)


class PaymentView(View):
    @check_user
    def patch(self, request):
        try:
            data          = json.loads(request.body)
            user          = request.user
            user_address  = user.address
            order_address = data.get('address')

            if user_address is None:
                User.objects.filter(id=user.id).update(address=order_address)
                return JsonResponse({"message": "SUCCESS"}, status=200)

            else:
                order_address = user_address
                User.object.filter(id=user.id).update(address=order_address)
                return JsonResponse({"message": "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"error": "INVALID_ADDRESS"}, status=400)


    @check_user
    def get(self, request):
        try:
            user    = request.user
            carts   = Cart.objects.filter(user=user)
            coupons = UserCoupon.objects.filter(user=user).select_related('coupon')

            carts_list = [{
                "product"       : cart.product.name,
                "price"         : cart.product.price,
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

        except Cart.DoesNotExist:
            return JsonResponse({"error": "INVALID_CART"}, status=400)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)