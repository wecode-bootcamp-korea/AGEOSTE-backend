import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count, Avg

from .models          import Product, Review, Reply, ProductColorImage, SubCategory
from user.utils       import check_user

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

            PAGE_COUNT = 20
            end_page   = page * PAGE_COUNT
            start_page = end_page - PAGE_COUNT
            
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
                'PRODUCT_COUNT : ' : products.count(),
                'PRODUCTS_LIST : ' : product_list},
                status=200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)


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
                } for product in subcategory.products.prefetch_related(
                    'productcolorimages__image', 'reviews'
                ).annotate(score_avg = Avg('reviews__score'), color_count=Count('colors', distinct=True))][:4]
            } for subcategory in subcategories]

            return JsonResponse({
                'SUB_CATEGORY_LIST' : subcategory_items},
                status=200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product            = Product.objects.get(id=product_id)
            review_score_avg   = product.reviews.aggregate(review_score_avg = Avg('score'))
            productcolorimages = ProductColorImage.objects.filter(product=product)

            color_images = [{
                'color_name' : color_name['color__name'],
                'img' : [
                    color_image.image.image_url 
                for color_image in productcolorimages.filter(color__name=color_name['color__name']).select_related('image')
            ]} for color_name in productcolorimages.values('color__name').distinct()]
            
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
            
            return JsonResponse({'product' : product_info},status = 200)

        except Product.DoesNotExist:
            return JsonResponse({'MESSAGE' : "Product does not exist"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

class ProductSearchView(View):
    def get(self, request):
        try:
            page     = int(request.GET.get('page', 1))
            word     = request.GET.get('word', None)
            hashtags = request.GET.getlist('hashtags', None)

            filter_set = {}

            if word:
                filter_set['name__icontains'] = word

            if hashtags:
                filter_set['hashtags__name__in'] = hashtags

            products = Product.objects.filter(**filter_set
            ).prefetch_related(
                'productcolorimages__image', 'reviews'
            ).annotate(score_avg = Avg('reviews__score'),color_count=Count('colors', distinct=True)) 

            PAGE_COUNT = 20
            end_page   = page * PAGE_COUNT
            start_page = end_page - PAGE_COUNT

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
                status=200
            )
        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

class ReviewView(View):
    @check_user
    def post(self, request, product_id):
        try:
            data = json.loads(request.body)

            Review.objects.create(
                user        = request.user,
                product     = Product.objects.get(id=product_id),
                score       = data['score'],
                description = data['description'],
                image_url   = data.get('image_url', None),
            )
            return JsonResponse({'MESSAGE':'Create review'}, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE':"KEY_ERROR"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

    @check_user
    def put(self, request, product_id, review_id):
        try:
            data   = json.loads(request.body)
            review = Review.objects.get(user = request.user, id = review_id)

            review.score       = data.get('score', review.score)
            review.description = data.get('description', review.description)
            review.image_url   = data.get('image_url', review.image_url)
            review.save()

            return JsonResponse({'MESSAGE':'리뷰를 수정하였습니다.'}, status=200) 

        except Review.DoesNotExist:
            return JsonResponse({'MESSAGE':"Review does not exist"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

    @check_user
    def delete(self, request, product_id, review_id):
        try:
            Review.objects.get(id=review_id, user=request.user).delete()
            return JsonResponse({'MESSAGE':'Delete review'}, status=200) 

        except Review.DoesNotExist:
            return JsonResponse({'MESSAGE':"Review does not exist"}, status=400)


class ReplyView(View):
    def get(self, request, product_id, review_id, reply_id):
        try:
            replies = Reply.objects.filter(review_id = review_id).select_related('user')

            reply_list = [{
                'user_name' : reply.user.name,
                'comment'   : reply.comment, 
            }for reply in replies]

            return JsonResponse({'REPLY_LIST': reply_list}, status=200)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

    # @check_user
    def post(self, request, product_id, review_id):
        try:
            data = json.loads(request.body)

            Reply.objects.create(
                user      = request.user,
                review_id = review_id,
                comment   = data['comment']
            )
            return JsonResponse({"MESSAGE": "Create reply"}, status=201)
        
        except Review.DoesNotExist:
            return JsonResponse({'MESSAGE':"Review does not exist"}, status=400)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

    @check_user
    def put(self, request, product_id, review_id, reply_id):
        try:
            data          = json.loads(request.body)
            reply         = Reply.objects.get(user = request.user, id = reply_id)
            reply.comment = data.get('comment', reply.comment)
            reply.save()

            return JsonResponse({"MESSAGE": "댓글을 수정하였습니다."}, status=200)

        except Reply.DoesNotExist:
            return JsonResponse({'MESSAGE':"Reply does not exist"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)

    @check_user
    def delete(self, request, product_id, review_id, reply_id):
        try:
            Reply.objects.get(user = request.user, id = reply_id).delete()
            return JsonResponse({"MESSAGE": "Delete reply"}, status=200)

        except Reply.DoesNotExist:
            return JsonResponse({'MESSAGE':"Reply does not exist"}, status=400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : e.args[0]}, status=400)