from django.urls import path

from .views      import ProductListView, ProductDetailView, ProductCategoryView

urlpatterns = [
    path('', ProductListView.as_view()),
    path('/<str:menu>', ProductCategoryView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
]