from celery import shared_task
from products.models import Product
from django.core.cache import cache




@shared_task
def product_cache_update():

    try:
        products = Product.objects.all()
        cache.delete('product_list')
        cache.set('product_list', list(products), timeout=60)
        # Assuming update_cache is a method to refresh the cache
    except Exception as e:
        print(f"Error updating product cache: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    except Exception as e:
        print(f"Failed to update product cache: {str(e)}")