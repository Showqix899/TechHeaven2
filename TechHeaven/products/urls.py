from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import(
    product_list,
    product_detail,
    product_create,
    product_update,
    product_delete,
    product_search,
    category_add,
    color_add,
    list_categories_and_colors,
    delete_category,
    delete_color,
    add_brand,
    delete_brand,

)


urlpatterns = [
    path('', product_list, name='product_list'),
    path('product/<uuid:product_id>/', product_detail, name='product_detail'),
    path('product/create/', product_create, name='product_create'),
    path('product/update/<uuid:product_id>/', product_update, name='product_update'),
    path('product/delete/<uuid:product_id>/', product_delete, name='product_delete'),
    path('product/search/', product_search, name='search'),
    path('category/add/', category_add, name='category_add'),
    path('color/add/', color_add, name='color_add'),
    path('categories-colors/list/', list_categories_and_colors, name='list_categories_and_colors'),
    path('category/delete/<uuid:category_id>/', delete_category, name='delete_category'),
    path('color/delete/<uuid:color_id>/', delete_color, name='delete_color'),
    path('brand/add/',add_brand,name="add_brand"),
    path('brand/delete/<uuid:brand_id>/',delete_brand,name="delete_brand"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)