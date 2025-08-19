from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from activity_log.models import ActivityLog
from django.utils.timezone import now
from middleware.current_user import get_current_user
from .models import Order



# Activity log for product creation and update
@receiver(post_save, sender=Order)
def log_product_save(sender, instance, created, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    action = "order creation" if created else "order updation"
    event = f"placed order by {email}"

    ActivityLog.objects.create(
        user=user,
        event=event,
        action=action,
        payload={
            "order_Id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )

# Activity log for product delete
@receiver(post_delete, sender=Order)
def log_product_delete(sender, instance, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    ActivityLog.objects.create(
        user=user,
        event=f"order deleted by {email}",
        action="product deletion",
        payload={
            "order_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )
