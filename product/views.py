from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count, Avg

from .models          import Product

class ProductListView(View):
    def get(self, request, menu, sub_category):
        try:
            page     = int(request.GET.get('page', 1))
            order    = request.GET.get('order', 'id') # price, -price, score_avg
            colors   = request.GET.getlist('colors')
            sizes    = request.GET.getlist('sizes')
            hashtags = request.GET.getlist('hashtags')

            filter_set = {
                "sub_category__name" : sub_category,
                "menu__name"         : menu,
            }

            if colors:
                filter_set['productcolorimages__color__name__in'] = colors

            if sizes:
                filter_set['sizes__name__in'] = sizes

            if hashtags:
                filter_set['hashtags__name__in'] = hashtags
            
            products = Product.objects.filter(**filter_set
            ).prefetch_related('productcolorimages__image', 'reviews'
            ).annotate(score_avg = Avg('reviews__score'), color_count=Count('colors', distinct=True)
            ).order_by(order)

            page_count = 20
            end_page   = page * page_count
            start_page = end_page - page_count
            
            product_list = [{
                'id'               : product.id,
                'name'             : product.name,
                'price'            : product.price,
                'discount_rate'    : product.discount_rate,
                'review_score_avg' : product.score_avg,
                'thumbnail'        : product.productcolorimages.all()[0].image.image_url,
                'color_count'      : product.color_count,
            } for product in products[start_page:end_page]]

            return JsonResponse({
                'PRODUCT_COUNT' : products.count(),
                'PRODUCT_LIST'  : product_list},
                status = 200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product          = Product.objects.get(id=product_id)
            review_score_avg = product.reviews.aggregate(review_score_avg = Avg('score'))

            color_images = [{
                'color_name' : color_name['color__name'],
                'img' : [
                    color_image.image.image_url 
                for color_image in product.productcolorimages.filter(color__name=color_name['color__name']).select_related('image')
            ]} for color_name in product.productcolorimages.values('color__name').distinct()]
            
            review = [{
                "review"      : review.id,
                'user_name'   : review.user.name,
                'image_url'   : review.image_url, 
                'score'       : review.score,
                'description' : review.description,
                'created_at'  : review.created_at,
            } for review in product.reviews.select_related('user')]

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
            
            return JsonResponse({'PRODUCT_INFO' : product_info},status = 200)
        except Product.DoesNotExist():
            return JsonResponse({'MESSAGE' : "해당 제품이 존재하지 않습니다."}, status=401)
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)