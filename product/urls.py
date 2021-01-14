from django.urls import path

from .views      import ProductsListView, ProductDetailView


urlpatterns = [
    path('', ProductsListView.as_view()), 
    path('/<str:menu>/<str:sub_category>', ProductsListView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
]