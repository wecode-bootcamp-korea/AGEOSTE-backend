import jwt

from django.http import JsonResponse

from ageoste.settings import SECRET_KEY
from user.models      import User

def check_user(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token        = request.headers.get('Authorization')
            payload      = jwt.decode(token, SECRET, algorithms='HS256')
            user         = User.objects.get(id=payload['user_id'])
            request.user = user

        except User.DoesNotExist:
            return JSonResponse({"message": "존재하지 않는 유저입니다."}, status=401)

        except jwt.DecodeError:
            return JsonResponse({"message": "잘못된 token 입니다."}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper
