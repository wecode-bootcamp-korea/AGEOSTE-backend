from django.urls import path

from .views      import ProductsListView


urlpatterns = [
    path('', ProductsListView.as_view()), 
    path('/<str:menu>/<str:sub_category>', ProductsListView.as_view()),
]