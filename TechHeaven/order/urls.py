from django.urls import path
from .views import place_order,cancle_order,order_list

urlpatterns = [
        path('order/place/', place_order, name='place_order'),
        path('order/cancel/<uuid:order_id>/',cancle_order,name="order_cancle"),
        path('order/list/',order_list,name="order_list"),

]
