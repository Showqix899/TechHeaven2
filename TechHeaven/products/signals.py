from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from django.core.cache import cache
from activity_log.models import ActivityLog
from django.utils.timezone import now
from middleware.current_user import get_current_user

user = get_current_user()
# Cache update on product save
@receiver(post_save, sender=Product)
def update_cache_on_product_save(sender, instance, **kwargs):
    cache.delete('product_list')
    cache.set('product_list', list(Product.objects.all()), timeout=60)

    
    print('✅ Cache updated for product save.')

# Cache update on product delete
@receiver(post_delete, sender=Product)
def update_cache_on_product_delete(sender, instance, **kwargs):
    cache.delete('product_list')
    cache.set('product_list', list(Product.objects.all()), timeout=60)
    print('🗑️ Cache updated for product delete.')

# Activity log for product creation and update
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    action = "product creation" if created else "product updation"
    event = f"{instance.name} {'created' if created else 'updated'} by {email}"

    ActivityLog.objects.create(
        user=user,
        event=event,
        action=action,
        payload={
            "product_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )

# Activity log for product delete
@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    ActivityLog.objects.create(
        user=user,
        event=f"{instance.name} deleted by {email}",
        action="product deletion",
        payload={
            "product_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )
