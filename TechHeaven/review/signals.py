from activity_log.models import ActivityLog
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils.timezone import now
from middleware.current_user import get_current_user
from .models import ProductReview


@receiver(post_save, sender=ProductReview)
def log_review_save(sender, instance, created, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    action = "review creation" if created else "review updation"
    event = f"{instance.product.name} {'created' if created else 'updated'} by {email}"

    ActivityLog.objects.create(
        user=user,
        event=event,
        action=action,
        payload={
            "review_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )
    

@receiver(post_delete, sender=ProductReview)
def log_review_delete(sender, instance, **kwargs):
    user = get_current_user()
    email = user.email if user else "Anonymous"

    ActivityLog.objects.create(
        user=user,
        event=f"{instance.product.name} review deleted by {email}",
        action="review deletion",
        payload={
            "review_id": str(instance.id),
            "user": email,
            "time": str(now())
        }
    )