from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count, Avg

from .models          import Product

class ProductsListView(View):
    def get(self, request, menu, sub_category):
        try:
            products = Product.objects.filter(
                sub_category__name = sub_category, 
                sub_category__main_category__menu__name=menu
            ).prefetch_related('productcolorimages__image').annotate(color_count=Count('colors', distinct=True)) 

            product_list = []
            for product in products:
                review_score_avg = product.reviews.all().aggregate(review_score_avg = Avg('score'))
                product_dict = {
                    'id'               : product.id,
                    'name'             : product.name,
                    'price'            : product.price,
                    'discount_rate'    : product.discount_rate,
                    'review_score_avg' : review_score_avg['review_score_avg'],
                    'thumbnail'        : product.productcolorimages.all()[0].image.image_url,
                    'color_count'      : product.color_count,
                }

                product_list.append(product_dict)

            return JsonResponse({
                'products_cnt' : products.count(),
                'products'     : product_list},
                status = 200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)


class ProductView(View):
    def get(self, request, product_id):
        try:
            product          = Product.objects.get(id=product_id)
            review_score_avg = product.reviews.all().aggregate(review_score_avg = Avg('score'))
            
            color_images = [{
                'color_name' : color_image.color.name,
                'image_url'  : color_image.image.image_url
            } for color_image in product.productcolorimages.all().prefetch_related('color','image')]

            review = [{
                'user_name'   : review.user.name,
                'image_url'   : review.image_url, 
                'score'       : review.score,
                'description' : review.description,
                'created_at'  : review.created_at,
            } for review in product.reviews.all().select_related('user')]

            product_info = {
                "name"             : product.name,
                "code"             : product.code,
                "description"      : product.description,
                "price"            : product.price,
                "sail_percent"     : product.discount_rate,
                "review_score_avg" : int(round(review_score_avg['review_score_avg'],0)),
                "hashtags"         : [hashtag.name for hashtag in product.hashtags.all()],
                "sizes"            : [size.name for size in product.sizes.all()],
                "color_images"     : color_images,
                "review"           : review,
            }
            
            return JsonResponse({'product' : product_info},status = 200)
        except Product.DoesNotExist():
            return JsonResponse({'MESSAGE' : "해당 제품이 존재하지 않습니다."}, status=401)
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

        