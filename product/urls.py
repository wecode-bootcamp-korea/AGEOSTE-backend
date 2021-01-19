from django.urls import path

from .views      import ProductListView, ProductDetailView, ReviewView, ReplyView


urlpatterns = [
    path('/<int:product_id>/review/<int:review_id>/reply/<int:reply_id>', ReplyView.as_view()),
    path('/<int:product_id>/review/<int:review_id>/reply', ReplyView.as_view()),
    path('/<int:product_id>/review/<int:review_id>', ReviewView.as_view()),
    path('/<int:product_id>/review', ReviewView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
    path('/<str:menu>/<str:sub_category>', ProductListView.as_view()),
]