from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count

from .models          import Product

class ProductsListView(View):
    def get(self, request, menu, sub_category):
        try:
            products = Product.objects.filter(
                sub_category__name=sub_category, 
                sub_category__main_category__menu__name=menu
            ).prefetch_related('productcolorimages').annotate(color_count=Count('colors', distinct=True)) 

            product_list = []
            for product in products:
                product_dict = {
                    'id'               : product.id,
                    'name'             : product.name,
                    'price'            : product.price,
                    'discount_rate'    : product.discount_rate,
                    'review_score_avg' : 3, # 리뷰의 평균점수, 이후 리뷰API 만들면서 구현 예정
                    'thumbnail'        : product.productcoloriages.get(id=1).image.image_url,
                    'color_count'      : product.color_count,
                }

                product_list.append(product_dict)

            return JsonResponse(
                {'products_cnt' : products.count(),
                'products'      : product_list},
                status = 200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE':(e.args[0])}, status=400)

              
# logger