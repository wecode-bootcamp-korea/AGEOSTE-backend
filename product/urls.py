from django.urls import path

from .views      import ProductListView, ProductDetailView, ReviewView, ReviewReplyView

urlpatterns = [
    path('/<str:menu>/<str:sub_category>', ProductListView.as_view()),
    path('/<int:product_id>', ProductDetailView.as_view()),
    path('review', ReviewView.as_view()),
    path('review/<int:review_id>', ReviewView.as_view()),
    # path('/review-reply', ReviewReplyView.as_view()),
    # path('/review-reply/<int:review_id>', ReviewReplyView.as_view()),
]