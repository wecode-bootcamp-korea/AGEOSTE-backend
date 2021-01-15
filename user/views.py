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

            if date_of_birth is not None:
                if len(date_of_birth) != 8 :
                       return JsonResponse({"error": "생년월일은 8자리의 숫자만 입력 가능합니다."}, status=400)
                date_of_birth = str(date_of_birth)
                date_of_birth = date_of_birth[:4] + '-' + date_of_birth[4:6] + '-' + date_of_birth[6:]

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

            return HttpResponse(status=201)

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

            if bcrypt.checkpw(password.encode('utf-8'), user_password.encode('utf-8')) is True:
                payload = {"user_id": user.id}
                token   = jwt.encode(payload, SECRET, algorithm='HS256')
                return JsonResponse({"token": token}, status=200)
            return JsonResponse({"error": "아이디 또는 비밀번호를 다시 확인하세요."}, status=401)

        except KeyError:
            return JsonResponse({"error": "KEY_ERROR"}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "존재하지 않는 아이디입니다."}, status=401)


