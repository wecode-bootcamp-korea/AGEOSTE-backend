from django.http.response import Http404
from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count

from .models          import Product

class ProductsListView(View):
    def get(self, request):
        menu         = request.GET.get('menu', None)
        sub_category = request.GET.get('sub_category', None)

        if sub_category: # 메뉴+카테고리를 입력받았을 경우. 이후 카테고리를 입력하지 않고, 메뉴만 검색했을 경우의 수 추가예정

            # prefetch_realted, annotate 사용했는데 잘 쓴건지 모르겠네요...
            products     = Product.objects.filter(sub_category__name=sub_category, sub_category__main_category__menu__name=menu).prefetch_related('productcolorimages').annotate(color_count=Count('colors', distinct=True)) 
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

        return Http404