# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('payment/card/<uuid:order_id>/', views.stripe_payment, name='stripe_payment'),
    path('payment/success/<uuid:order_id>/', views.stripe_success, name='stripe_success'),
    path('payment/list/',views.payment_list,name="payment_list"),
]
