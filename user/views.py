import json
import re
import bcrypt
import jwt

from django.http                    import JsonResponse, HttpResponse
from django.db                      import transaction
from django.views                   import View
from django.core.exceptions         import ValidationError, ObjectDoesNotExist
from django.shortcuts               import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http              import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail               import EmailMessage
from django.utils.encoding          import force_bytes, force_text

from .models     import User, UserCoupon, Coupon
from .tokens     import account_activation_token
from my_settings import SECRET, EMAIL
from .utils      import check_user, active_message
from .validators import validate_email, validate_password, validate_phone_number, validate_birth


class SignUpView(View):
    @transaction.atomic
    def post(self, request):
        try:
            data          = json.loads(request.body)
            name          = data['name']
            email         = data['email']
            password      = data['password']
            phone_number  = data['phone_number']
            date_of_birth = data.get('date_of_birth')

            if not name:
                return JsonResponse({"error": "KEY_ERROR"})

            if not validate_email(email):
                return JsonResponse({"error": "INVALID_EMAIL"}, status=400)

            if not validate_password(password):
                return JsonResponse({"error": "INVALID_PASSWORD"}, status=400)

            if not validate_phone_number(phone_number):
                return JsonResponse({"error": "INVALID_PHONE_NUMBER"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "EXIST_EMAIL"}, status=400)

            if User.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({"error": "EXIST_PHONE_NUMBER"}, status=400)

            if date_of_birth:
                if not validate_birth(date_of_birth):
                    return JsonResponse({"error": "INVALID_BIRTH"}, status=400)
                date_of_birth = str(date_of_birth)
                date_of_birth = f'{date_of_birth[:4]}-{date_of_birth[4:6]}-{date_of_birth[6:]}'

            encoded_pw = password.encode('utf-8')
            hashed_pw  = bcrypt.hashpw(encoded_pw, bcrypt.gensalt()).decode('utf-8')

            user = User(
                name          = name,
                email         = email,
                phone_number  = phone_number,
                date_of_birth = date_of_birth,
                password      = hashed_pw
            )
            user.full_clean()
            user.save()

            UserCoupon.objects.create(user_id = user.id, coupon_id =1)

            return JsonResponse({"message": "SUCCESS"}, status=201)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except ValidationError:
            return JsonResponse({"error": "VALIDATOR_ERROR"}, status=400)

        except json.decoder.JSONDecodeError:
            return JsonResponse({"error": "JSON_DECODE_ERROR"}, status=400)


class SignInView(View):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            email    = data['email']
            password = data['password']

            user          = User.objects.get(email=email)
            user_password = user.password

            if bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8')):
                payload = {"user_id": user.id}
                token   = jwt.encode(payload, SECRET, algorithm='HS256')
                return JsonResponse({"token": token, "message": "SUCCESS"}, status=200)
            return JsonResponse({"error": "INVALID_PASSWORD"}, status=401)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "INVALID_EMAIL"}, status=401)


class AccountView(View):
    @check_user
    def get(self, request):
        user                = request.user
        phone               = user.phone_number
        mypage_phone_number = f'{phone[:3]}-{phone[3:7]}-{phone[7:]}'

        accounts = {
            'name'         : user.name,
            'email'        : user.email,
            'phone_number' : mypage_phone_number,
            'date_of_birth': user.date_of_birth,
            'address'      : user.address,
            'membership'   : {
                'grade'        : user.membership.grade,
                'discount_rate': user.membership.discount_rate
            },
            'favorite_shop' : None
        }

        if user.favorite_shop:
            accounts['favorite_shop'] = {
                'id'           : user.favorite_shop.id,
                'city'         : user.favorite_shop.city,
                'name'         : user.favorite_shop.name,
                'address'      : user.favorite_shop.address,
                'phone_number' : user.favorite_shop.phone_number,
                'work_day'     : user.favorite_shop.work_day
            }

        return JsonResponse({"accounts": accounts}, status=200)


    @check_user
    def put(self, request):
        data            = json.loads(request.body)
        user            = request.user
        new_pw          = data.get('password')
        current_pw      = user.password
        existed_shop    = user.favorite_shop
        changed_shop    = data.get('favorite_shop')
        changed_address = data.get('address')

        if new_pw:
            if not validate_password(new_pw):
                return JsonResponse({"error": "INVALID_PASSWORD"}, status=400)
            if bcrypt.checkpw(new_pw.encode('utf-8'), current_pw.encode('utf-8')):
                return JsonResponse({"error": "EXIST_PASSWORD"}, status=400)

            encoded_pw = new_pw.encode('utf-8')
            hashed_pw  = bcrypt.hashpw(encoded_pw, bcrypt.gensalt()).decode('utf-8')
            User.objects.filter(id = user.id).update(password = hashed_pw)
            return JsonResponse({"message" : "SUCCESS"}, status=200)

        if changed_shop:
            User.objects.filter(id = user.id).update(favorite_shop = changed_shop)
            return HttpResponse(status=200)

        if change_address:
            User.objects.filter(id = user.id).update(address = changed_address)
            return HttpResponse(status=200)


class EmailAuthView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            email   = data['email']
            user    = User.objects.get(email=email)
            user_id = user.id

            current_site = get_current_site(request)
            domain       = current_site.domain

            uidb64       = urlsafe_base64_encode(force_bytes(user_id))
            token        = account_activation_token.make_token(user)
            message_data = active_message(domain, uidb64, token)

            mail_title = "이메일 인증을 완료해주세요"
            mail_to    = data['email']
            email      = EmailMessage(mail_title, message_data, to=[mail_to])
            email.send()

            return JsonResponse({"message": "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except TypeError:
            return JsonResponse({"error": "TYPE_ERROR"}, status=400)

        except ValidationError:
            return JsonResponse({"error": "VALIDATION_ERROR"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "NON_EXIST_USER"}, status=400)

        except MultipleObjectsReturned:
            return JsonResponse({"error": "MULTIPLE_OBJECTS_ERROR"}, status=400)


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid  = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                User.objects.filter(pk=uid).update(is_active=True, membership_id=2)
                return redirect(EMAIL['REDIRECT_PAGE'])
            return JsonResponse({"error": "AUTH_FAIL"}, status=400)

        except ValidationError:
            return JsonResponse({"error": "TYPE_ERROR"}, status=400)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)


class KakaoSignInView(View):
    def post(self, request):
        try:
            access_token = request.headers.get('Authorization')
            kakao_data = request.get("https://kapi.kakao.com/v2/user/me",
                                     headers={"Authorization": f"Bearer {access_token}"}).json()

            kakao_id = kakao_data['id']
            kakao_name = kakao_data['kakao_account']['profile']['nickname']
            kakao_email = f'{kakao_name}@{kakao_id}.{kakao_id}'

            if User.objects.filter(email=kakao_id).exists():
                user = User.objects.get(email=kakao_email)
                token = jwt.encode({"user":user.id}, SECRET, algorithm='HS256')
                return JsonResponse({"token": token}, status=200)

            else:
                data = json.loads(request.body)
                User.objects.create(
                    email = kakao_email,
                    name = kakao_name
                )

                user = User.objects.get(email = kakao_email)
                token = jwt.encode({"user":user.id}, SECRET, algorithm='HS256')

                return JsonResponse({"token": token}, status=200)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"})


class CouponView(View):
    @check_user
    def get(self, request):
        user = request.user
        coupons = UserCoupon.objects.filter(user=user).select_related('coupon')

        coupons_list = [{
            "coupon" : coupon.coupon.name,
            "discount_rate" : coupon.coupon.discount_rate,
            "description" : coupon.coupon.description
        } for coupon in coupons]

        return JsonResponse({"coupons_list": coupons_list}, status=200)
