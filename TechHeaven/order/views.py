from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.models import CartItem, Cart  # Adjust as needed
from cart.views import get_cart  # Assuming you use this helper
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

#order placing
@login_required
def place_order(request):
    cart= get_cart(request)


    cart_items=CartItem.objects.filter(cart=cart,is_selected=True) #get all the selected item

    if not cart_items.exists():
        return redirect('view_cart')
    
    if not cart_items:
        return render(request, 'accounts/error_message.html', {
            'message': 'Your cart is empty. Please add items to your cart before placing an order.'
        })
    
    order= Order.objects.create(user=request.user)

    total = 0

    for item in cart_items:

        #checking if stock available
        if item.quantity > item.product.stock:
            return HttpResponse(f"not enough stock left for {item.product.name}")
        
        subtoral = item.product.price * item.quantity
        total += subtoral
        
        
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_order=item.product.price
        )
    order.total_amount = total
    order.order_type = 'multiple'  # Indicating this is a multiple item order
    order.save()

    # Clear the cart after placing the order
    return render(request, 'payment/select_payment.html', {
        'order': order,
        'total_amount': total,
    })



#order cancle view
@login_required
def cancle_order(request,order_id):
    try:

        order=Order.objects.get(id=order_id)
        order_items=OrderItem.objects.filter(order=order)
        print(order_items) #for dibuggin
        order_items.delete()

        return redirect('view_cart')

    except Order.DoesNotExist:

        return HttpResponse("Order not Found")
    except Exception as e:

        return HttpResponse(f"{e}")


#order list
def order_list(request):

    if not request.user.role == "ADMIN":
        return HttpResponse("need to be an Admin. You are not allowed")
    
    total_order_amount=0
    try:

        orders=Order.objects.all().order_by('-created_at')
        order_items=Order.objects.all().order_by('-created_at')

        for item in orders:

            total_order_amount+=item.total_amount

        return render (request,'order/order_list.html',{
            'orders':orders,
            'total_order_amount':total_order_amount,
            'orders_item':order_items

        })
    except Order.DoesNotExist:

        return render(request,'accounts/error_message.html',{'message':'404 Nothing'})
