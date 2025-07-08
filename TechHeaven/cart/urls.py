from django.urls import path
from .views import add_to_cart, view_cart, remove_cart_item, update_cart_item, toggle_item_selection,all_item_selection
urlpatterns = [
    path('cart/add/<uuid:product_id>/',add_to_cart , name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<uuid:item_id>/', remove_cart_item, name='remove_cart_item'),
    path('cart/update/<uuid:item_id>/',update_cart_item, name='update_cart_item'),
    path('cart/toggle/<uuid:item_id>/', toggle_item_selection, name='toggle_item_selection'),
    path('cart/all-select/',all_item_selection,name="all_item_select"),
]
