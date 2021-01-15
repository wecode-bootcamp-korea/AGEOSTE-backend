from django.urls import path

from .views      import ProductListView, ProductDetailView, ProductCategoryView

urlpatterns = [
    path('/<str:menu>/<str:sub_category>', ProductListView.as_view()),
    path('/<str:menu>', ProductCategoryView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
]