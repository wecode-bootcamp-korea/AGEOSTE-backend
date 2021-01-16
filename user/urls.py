from django.urls import path
from .views      import SignupView, SigninView, AccountView

urlpatterns = [
    path('/signup', SignupView.as_view()),
    path('/signin', SigninView.as_view()),
    path('/account', AccountView.as_view())
]
