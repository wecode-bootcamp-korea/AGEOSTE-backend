import jwt

from django.http import JsonResponse

from ageoste.settings import SECRET_KEY
from user.models      import User

def check_user(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token        = request.headers.get('Authorization')
            payload      = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            user         = User.objects.get(id=payload['user_id'])
            request.user = user

        except User.DoesNotExist:
            return JsonResponse({"message": "존재하지 않는 유저입니다."}, status=401)

        except jwt.DecodeError:
            return JsonResponse({"message": "잘못된 token 입니다."}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper

def active_message(domain, uidb64, token):
    return f"아래 링크를 클릭하면 회원가입 인증이 완료됩니다.\n\n 회원가입링크 : http://{domain}/user/emailauth/activate/{uidb64}/{token}\n\n감사합니다."
