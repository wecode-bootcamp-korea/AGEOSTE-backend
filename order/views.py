import json

from django.views     import View
from django.http      import JsonResponse

from .models          import Cart
from product.models   import Product, Color, Size, Image
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
            data       = json.loads(request.body)
            size       = Size.objects.get(name=data['size']) # 이 부분 create에서 한줄로 쓰는 방법, id를 입력받는것은 힘듬. name값으로 무조건 받아야 하는 상황.
            color      = Color.objects.get(name=data['color'])
            image      = Image.objects.get(image_url=data['image']) # 프론트에서 이미지url보내는 방향으로 이야기, or product -> productcolorimages(product, color로 검색) -> image
            product_id = data['product_id']

            cart, _ = Cart.objects.get_or_create(
                user       = request.user,
                product_id = product_id, 
                size       = size,
                color      = color,
                thumbnail  = image,
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