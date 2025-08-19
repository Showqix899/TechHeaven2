from django.urls import path

from .views import post_review

urlpatterns = [
    path('post_review/<uuid:product_id>/', post_review, name='post_review'),
]