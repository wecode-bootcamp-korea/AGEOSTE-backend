from django.urls import path

from .views      import ProductsListView


urlpatterns = [
    path('', ProductsListView.as_view()), # /메뉴이름/카테고리이름 or /메뉴이름으로 받을예정
]

