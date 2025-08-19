from django.shortcuts import render,HttpResponse
from order.models import Order
from django.contrib.auth.decorators import login_required

import stripe
from django.conf import settings

from cart.models import Cart, CartItem  # Adjust as needed
from cart.views import get_cart  # Assuming you use this helper
from django.shortcuts import redirect,get_object_or_404
from .tasks import send_payment_confirmation_email,cart_item_deletion,stock_updation
from .models import PaymentHistory

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY #stripe secret key


@login_required
def select_payment_method(request,order_id):

    # Fetch the order based on the provided order_id and the logged-in user
    try:
        order = Order.objects.get(id=order_id, user=request.user)


        if request.method == 'POST':

            method = request.POST.get('payment_method')

            if method == 'stripe':
                # Redirect to Stripe payment page
                return render(request, 'payment/stripe_payment.html', {'order': order})
            elif method == 'ssl_commerz':
                # Redirect to SSL Commerz payment page
                return render(request, 'payment/ssl_commerz_payment.html', {'order': order})
        
        # Render the payment method selection page
        return render(request, 'payment/select_payment.html', {'order': order})
            
    except Order.DoesNotExist:

        return render(request,'accounts/error_message.html',{'message':'Order not found or you do not have permission to view this order.'})
    

#stripe payment view
@login_required
def stripe_payment(request,order_id):

    #fetch order based on order_id and user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Create a stripe payment intent
    if not order.is_paid:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount* 100),
            currency='bdt',  # Change to your desired currency
            metadata={
                'order_id': str(order.id),
                'user_id': request.user.id,
            }
        )
        order.payment_id = intent.id
        
        order.save()
        payment_history=PaymentHistory.objects.create(
            user=request.user,
            payment_method="Stripe",
            order=order,
            total_amount=int(order.total_amount),
            status="pending"
        )
        payment_history.save()
    else:
        intent = stripe.PaymentIntent.retrieve(order.payment_id)

    
    
    return render(request, 'payment/stripe_payment.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Pass the public key to the template
        'client_secret': intent.client_secret,  # Pass the client secret for the payment intent
        'order':order
    })

    

#after payment success
def stripe_success(request,order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart=get_cart(request)
    message=""
    payemnt_history=PaymentHistory.objects.get(order=order_id)


    if not order.is_paid:
        # Mark the order as paid
        order.is_paid = True
        order.status = 'Paid'
        order.payment_method = 'Stripe'
        order.save()
        payemnt_history.status="success"
        payemnt_history.save()
        user_email=request.user.email
        message=f"payment was successfull. An email has been sent to {request.user.email}"

        stock_updation.delay(order_id) #to update stock
        send_payment_confirmation_email.delay(order.id,cart.id,user_email) #emailing user the payment info



        try:
            # If the order is for multiple items, clear the cart
            cart = get_cart(request)
            cart_item_deletion.delay(cart.id)
            print("Cart items deleted successfully.")
            
        except Exception as e:
            print(f"showqi-> deleting cart item: {e}")
        
    else:
        message="Al ready paid"

        
    return render(request, 'payment/success.html', {'order': order,'message':message})


def stripe_cancel(request):
    return render(request, 'payments/cancel.html')


from django.core.paginator import Paginator
from django.http import JsonResponse



# List all payments for admin
@login_required
def payment_list(request):
    if request.user.role != "ADMIN":
        return HttpResponse("Need to be an Admin. You are not allowed")

    # Calculate total sell amount by looping, like you had before

    query = request.GET.get('query', '').strip()

    if query:
        # Filter payment history based on user email
        payment_list = PaymentHistory.objects.filter(user__email__icontains=query).order_by('-created_at')
    else:
        # Fetch all payment history records
        payment_list = PaymentHistory.objects.all().order_by('-created_at')

    
    total_sell_amount = 0
    for item in payment_list:
        total_sell_amount += item.total_amount

    # Pagination: always 5 per page
    paginator = Paginator(payment_list, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'payment/payment_list.html', {
        'total_order_amount': total_sell_amount,
        'orders_item': page_obj,  # paginated items
        'paginator': paginator,
        'page_obj': page_obj,
    })