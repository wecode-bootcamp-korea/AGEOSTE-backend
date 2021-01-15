from django.urls import path

from .views      import ProductListView, ProductDetailView, ProductSearchView

urlpatterns = [
    path('/<str:menu>/<str:sub_category>', ProductListView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
    path('/search', ProductSearchView.as_view()),
]