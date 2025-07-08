from cart.models import Cart, CartItem
from order.models import Order ,OrderItem
from products.models import Product
from accounts.task import email_send
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail




@shared_task
def send_payment_confirmation_email(order_id, cart_id, user_email):
    subject = "Stripe Payment Confirmation"
    message = ""

    try:
        cart_items = CartItem.objects.filter(cart_id=cart_id, is_selected=True)
        order = Order.objects.get(id=order_id)

        for item in cart_items:
            message += (
                f"Name: {item.product.name} - Quantity: {item.quantity} "
                f"- Total Price: {item.total_price()} BDT\n"
            )

        message += f"\nTotal Amount: {order.total_amount} BDT"

    except Exception as e:
        message = str(e)
        subject = "Stripe Payment Failed"

    # ✅ Make sure recipient email is in a list
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])


@shared_task
def cart_item_deletion(cart_id):

    try:

        cart_items=CartItem.objects.filter(cart=cart_id,is_selected=True)
        cart_items.delete()
    except Exception as e:

        print(str(e))




#stock updation
@shared_task
def stock_updation(order_id):
    try:
        order_items = OrderItem.objects.filter(order_id=order_id)

        for item in order_items:
            product = item.product
            product.stock = max(0, product.stock - item.quantity)  # Prevent negative stock
            product.save()
            print("stock updated")


    except Exception as e:
        return f"Stock update failed for order {order_id}: {str(e)}"