import json
import re
import bcrypt
import jwt

from django.http  import JsonResponse, HttpResponse
from django.views import View

from .models     import User
from my_settings import SECRET


class SignupView(View):
    def post(self, request):
        try:
            data          = json.loads(request.body)
            name          = data.get('name')
            email         = data['email']
            phone_number  = data['phone_number']
            date_of_birth = data.get('date_of_birth')
            password      = data['password']

            email_rule        = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            password_rule     = re.compile('^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$')
            phone_number_rule = re.compile('010-?[0-9]{4}-?[0-9]{4}')

            if not email or not phone_number or not password:
                return JsonResponse({"error": "KEY_ERROR"})

            if not email_rule.match(email):
                return JsonResponse({"error": "양식에 맞지 않는 이메일입니다."}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "이 주소의 아이디가 이미 존재합니다."}, status=400)

            if not password_rule.match(password):
                return JsonResponse({"error": "비밀번호는 문자, 숫자, 특수문자가 포함되어야 합니다"}, status=400)

            if not phone_number_rule.match(phone_number):
                return JsonResponse({"error": "양식에 맞지 않는 휴대폰 번호입니다."}, status=400)

            if User.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({"error": "이미 존재하는 휴대폰 번호 입니다."}, status=400)

            encoded_pw = password.encode('utf-8')
            hashed_pw = bcrypt.hashpw(encoded_pw, bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                name          = name,
                email         = email,
                phone_number  = phone_number,
                date_of_birth = date_of_birth,
                password      = hashed_pw
            )

            return HttpResponse(status=200)

        except Exception as e:
            return JsonResponse({"error":(e.args[0])}, status=500)
