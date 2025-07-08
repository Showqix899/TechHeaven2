from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from activity_log.models import ActivityLog
from django.utils.timezone import now
from middleware.current_user import get_current_user
from .models import PaymentHistory



# Activity log for product creation and update
@receiver(post_save, sender=PaymentHistory)
def log_product_save(sender, instance, created, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    action = "Payment creation" if created else "Payment updation"
    event = f"payment recieved by {user.email}"

    ActivityLog.objects.create(
        event=event,
        action=action,
        payload={
            "payment_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )

# Activity log for product delete
@receiver(post_delete, sender=PaymentHistory)
def log_product_delete(sender, instance, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    ActivityLog.objects.create(
        event=f"payment deleted by {email}",
        action="Payment deletion",
        payload={
            "payment_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )
