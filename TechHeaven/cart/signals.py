from activity_log.models import ActivityLog
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cart.models import Cart, CartItem

@receiver(post_save, sender=Cart)
def log_cart_save(sender, instance, created, **kwargs):
    event = 'Cart Created' if created else 'Cart Updated'
    ActivityLog.objects.create(
        user=instance.user if instance.user else None,
        event=event,
        action='save',
        payload={'cart_id': str(instance.id), 'user_id': str(instance.user.id)},
    )


@receiver(post_delete, sender=Cart)
def log_cart_delete(sender, instance, **kwargs):
    user= instance.user if instance.user else None
    ActivityLog.objects.create(
        user=user,
        event='Cart Deleted',
        action='delete',
        payload={'cart_id': str(instance.id), 'user_id': str(instance.user.id)},
    )


@receiver(post_save, sender=CartItem)
def log_cart_item_save(sender, instance, created, **kwargs):
    event = 'Cart Item Added' if created else 'Cart Item Updated'
    ActivityLog.objects.create(
        user=instance.cart.user if instance.cart.user else None,
        event=event,
        action='save',
        payload={
            'cart_item_id': str(instance.id),
            'cart_id': str(instance.cart.id),
            'user_id': str(instance.cart.user.id) if instance.cart.user else None
        },
    )


@receiver(post_delete, sender=CartItem)
def log_cart_item_delete(sender, instance, **kwargs):
    user = instance.cart.user if instance.cart.user else None
    ActivityLog.objects.create(
        user=user,
        event='Cart Item Deleted',
        action='delete',
        payload={
            'cart_item_id': str(instance.id),
            'cart_id': str(instance.cart.id),
            'user_id': str(instance.cart.user.id) if instance.cart.user else None
        },
    )
    