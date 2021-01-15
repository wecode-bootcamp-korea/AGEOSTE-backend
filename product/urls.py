from django.urls import path

from .views      import ProductsListView, ProductView

urlpatterns = [
    path('/<str:menu>/<str:sub_category>', ProductsListView.as_view()),
    path('/<int:product_id>', ProductView.as_view()),
]