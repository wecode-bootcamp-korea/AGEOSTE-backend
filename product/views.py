import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Count, Avg

from .models          import Product, Review, Reply
from user.utils       import check_user

class ProductListView(View):
    def get(self, request, menu, sub_category):
        try:
            print("!@@@")

            page     = int(request.GET.get('page', 1))
            products = Product.objects.filter(
                sub_category__name = sub_category, 
                sub_category__main_category__menu__name=menu
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


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            print("@@@@@")
            
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
            return JsonResponse({'MESSAGE':'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE':"KEY_ERROR"}, status = 400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

    @check_user
    def put(self, request, product_id, review_id):
        try:
            data   = json.loads(request.body)
            review = Review.objects.get(user = request.user, id = review_id)

            review.score       = data.get('score', review.score)
            review.description = data.get('description', review.description)
            review.image_url   = data.get('image_url', review.image_url)
            review.save()

            return JsonResponse({'MESSAGE':'MODIFY REVIEW'}, status=200) 

        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

    @check_user
    def delete(self, request, product_id, review_id):
        try:
            Review.objects.get(id=review_id, user=request.user).delete()
            return JsonResponse({'MESSAGE':'Review was deleted'}, status=200) 

        except Review.DoesNotExist():
            return JsonResponse({'MESSAGE':"리뷰가 존재하지 않습니다."}, status = 400)

class ReplyView(View):
    def get(self, request, product_id, review_id, reply_id):
        try:
            replies = Reply.objects.filter(review_id = review_id).select_related('user')

            result = [{
                'user_name' : reply.user.name,
                'comment'   : reply.comment, 
            }for reply in replies]

            return JsonResponse({'Reply': result}, status = 200)

        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

    @check_user
    def post(self, request, product_id, review_id):
        try:
            data = json.loads(request.body)

            Reply.objects.create(
                user     = request.user,
                review   = Review.objects.get(id = review_id),
                comment  = data['comment']
            )
            return JsonResponse({"MESSAGE": "SUCCESS"}, status = 200)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status = 400)

        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

    @check_user
    def put(self, request, product_id, review_id, reply_id):
        try:
            data  = json.loads(request.body)
            reply = Reply.objects.get(user = request.user, id = reply_id)

            reply.comment = data.get('comment', reply.comment)
            reply.save()

            return JsonResponse({"MESSAGE": "SUCCESS"}, status = 200)

        except Exception as e:
            return JsonResponse({'MESSAGE' : (e.args[0])}, status=400)

        except Reply.DoesNotExist():
            return JsonResponse({'MESSAGE':"댓글이 존재하지 않습니다."}, status = 400)

    @check_user
    def delete(self, request, product_id, review_id, reply_id):
        try:
            Reply.objects.get(user = request.user, id = reply_id).delete()
            return JsonResponse({"MESSAGE": "Reply was deleted"}, status = 200)

        except Reply.DoesNotExist():
            return JsonResponse({'MESSAGE':"댓글이 존재하지 않습니다."}, status = 400)