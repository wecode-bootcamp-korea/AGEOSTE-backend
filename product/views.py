from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count, Avg

from .models          import Product, SubCategory

class ProductListView(View):
    def get(self, request, menu, sub_category):
        try:
            page     = int(request.GET.get('page', 1))
            products = Product.objects.filter(
                sub_category__name = sub_category, 
                menu__name         = menu
            ).prefetch_related('productcolorimages__image', 'reviews').annotate(score_avg = Avg('reviews__score'),color_count=Count('colors', distinct=True)) 

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
                'products_cnt' : products.count(),
                'products'     : product_list},
                status = 200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)


class ProductCategoryView(View):
    def get(self, request, menu):
        try:
            subcategories = SubCategory.objects.filter(menu__name=menu).prefetch_related('products')

            subcategory_items = [{
                'subcategory_name' : subcategory.name,
                'subcategory_item' : [{
                    'product_id'       : product.id,
                    'product_name'     : product.name,
                    'price'            : product.price,
                    'discount_rate'    : product.discount_rate,
                    'review_score_avg' : product.score_avg,
                    'thumbnail'        : product.productcolorimages.all()[0].image.image_url,
                    'color_count'      : product.color_count,
                } for product in subcategory.products.prefetch_related('productcolorimages__image', 'reviews').
                annotate(score_avg = Avg('reviews__score'), color_count=Count('colors', distinct=True))][:4]
            } for subcategory in subcategories]

            return JsonResponse({
                'subcategory_items' : subcategory_items},
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
                'color_name' : color_image.color.name,
                'image_url'  : color_image.image.image_url
            } for color_image in product.productcolorimages.select_related('color','image')]

            review = [{
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
            
            return JsonResponse({'product' : product_info},status = 200)
        except Product.DoesNotExist():
            return JsonResponse({'MESSAGE' : "해당 제품이 존재하지 않습니다."}, status=401)
        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)