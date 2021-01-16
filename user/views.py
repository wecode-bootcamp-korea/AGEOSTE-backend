import json
import re
import bcrypt
import jwt

from django.http            import JsonResponse, HttpResponse
from django.views           import View
from django.core.exceptions import ValidationError

from .models     import User
from my_settings import SECRET
from .utils      import check_user
from .validators import validate_email, validate_password, validate_phone_number


class SignupView(View):
    def post(self, request):
        try:
            data          = json.loads(request.body)
            name          = data['name']
            email         = data['email']
            password      = data['password']
            phone_number  = data['phone_number']
            date_of_birth = data.get('date_of_birth')

            if not validate_email(email):
                return JsonResponse({"error" : "양식에 맞지 않는 이메일입니다."}, status=400)

            if not validate_password(password):
                return JsonResponse({"error": "비밀번호는 문자, 숫자, 특수문자가 포함되어야합니다."}, status=400)

            if not validate_phone_number(phone_number):
                return JsonResponse({"error": "양식에 맞지 않는 휴대폰번호입니다."}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "이 주소의 아이디가 이미 존재합니다."}, status=400)

            if User.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({"error": "이미 존재하는 휴대폰 번호입니다."}, status=400)

            if date_of_birth and len(date_of_birth) != 8:
                return JsonResponse({"error": "생년월일은 8자리의 숫자만 입력 가능합니다."}, status=400)
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

            return JsonResponse({"message": "SUCCESS"}, status=201)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except ValidationError:
            return JsonResponse({"error": "VALIDATOR_ERROR"}, status=400)

        except json.decoder.JSONDecodeError:
            return JsonResponse({"error": "JSON_DECODE_ERROR"}, status=400)


class SigninView(View):
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
                return JsonResponse({"token": token}, status=200)
            return JsonResponse({"error": "아이디 또는 비밀번호를 다시 확인하세요."}, status=401)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "존재하지 않는 아이디입니다."}, status=401)


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
            'password'     : '********',
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

        return JsonResponse({"accounts" : accounts}, status=200)


    @check_user
    def put(self, request):
        data = json.loads(request.body)
        user = request.user
        changed_pw = data.get('password')
        existed_pw = user.password
        existed_shop = user.favorite_shop
        changed_shop = data.get('favorite_shop')
        changed_address = data.get('address')

        if changed_pw and not validate_password(changed_pw):
            return JsonResponse({"error" : "양식에 맞지 않는 비밀번호 입니다."}, status=400)

        if changed_pw and bcrypt.checkpw(changed_pw.encode('utf-8'), existed_pw.encode('utf-8')):
            return JsonResponse({"error" : "기존의 비밀번호와 같은 비밀번호로 변경할 수 없습니다."})

        if changed_pw:
            encoded_pw = changed_pw.encode('utf-8')
            hashed_pw  = bcrypt.hashpw(encoded_pw, bcrypt.gensalt()).decode('utf-8')
            User.objects.filter(id = user.id).update(password = hashed_pw)
            return JsonResponse({"message" : "비밀번호가 성공적으로 변경되었습니다."}, status=200)

        if changed_shop:
            User.objects.filter(id = user.id).update(favorite_shop = changed_shop)
            return HttpResponse(status=200)

        if change_address:
            User.objects.filter(id = user.id).update(address = changed_address)
            return HttpResponse(status=200)
