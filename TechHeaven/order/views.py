from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.models import CartItem, Cart  # Adjust as needed
from cart.views import get_cart  # Assuming you use this helper
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from userprofile.models import UserAddress
from django.contrib import messages
from .forms import OrderAddressForm  # Assuming you have this form defined
from django.core.paginator import Paginator
from django.http import JsonResponse

#order placing
# @login_required
# def place_order(request):
#     cart= get_cart(request)

#     cart_items=CartItem.objects.filter(cart=cart,is_selected=True) #get all the selected item

#     if not cart_items.exists():
#         return redirect('view_cart')
    
#     if not cart_items:
#         return render(request, 'accounts/error_message.html', {
#             'message': 'Your cart is empty. Please add items to your cart before placing an order.'
#         })
    
#     order= Order.objects.create(user=request.user)

#     total = 0

#     for item in cart_items:

#         #checking if stock available
#         if item.quantity > item.product.stock:
#             return HttpResponse(f"not enough stock left for {item.product.name}")
        
#         subtoral = item.product.price * item.quantity
#         total += subtoral
        
        
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price_at_order=item.product.price
#         )
#     order.total_amount = total
#     order.order_type = 'multiple'  # Indicating this is a multiple item order
#     order.save()

#     # Clear the cart after placing the order
#     return render(request, 'payment/select_payment.html', {
#         'order': order,
#         'total_amount': total,
#     })


@login_required
def place_order(request):
    cart = get_cart(request)
    cart_items = CartItem.objects.filter(cart=cart, is_selected=True)

    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f"Not enough stock left for {item.product.name}")
            return redirect('view_cart')

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items before placing an order.")
        return redirect('view_cart')

    if request.method == 'POST':
        form = OrderAddressForm(request.POST, user=request.user)
        if form.is_valid():
            existing_address = form.cleaned_data['existing_address']
            if existing_address:
                shipping_address = f"{existing_address.address_line1}"
                if existing_address.address_line2:
                    shipping_address += f", {existing_address.address_line2}"
                shipping_address += f", {existing_address.city}, {existing_address.state} - {existing_address.postal_code}, {existing_address.country}"
            else:
                shipping_address = f"{form.cleaned_data['new_address_line1']}, {form.cleaned_data['new_city']}, {form.cleaned_data['new_state']} - {form.cleaned_data['new_postal_code']}, {form.cleaned_data['new_country']}"

                

            # Create order
            order = Order.objects.create(user=request.user, shipping_address=shipping_address)

            total = 0
            for item in cart_items:
                if item.quantity > item.product.stock:
                    messages.error(request, f"Not enough stock left for {item.product.name}")
                    return redirect('view_cart')

                subtotal = item.product.price * item.quantity
                total += subtotal

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_order=item.product.price
                )

            order.total_amount = total
            order.order_type = 'multiple'
            order.save()

            # Clear cart items or cart here as needed

            return render(request, 'payment/select_payment.html', {
                'order': order,
                'total_amount': total,
            })

    else:
        form = OrderAddressForm(user=request.user)

    return render(request, 'order/place_order.html', {
        'cart_items': cart_items,
        'form': form
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
@login_required
def order_list(request):
    if request.user.role != "ADMIN":
        return HttpResponse("Need to be an Admin. You are not allowed")
    
    query = request.GET.get('query', '').strip()

    if query:
        orders = Order.objects.filter(user__email__icontains=query).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')

    total_order_amount = sum(order.total_amount for order in orders)

    paginator = Paginator(orders, 5)  # 5 orders per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'order/order_list.html', {
        'orders': page_obj,
        'total_order_amount': total_order_amount,
        'paginator': paginator,
        'page_obj': page_obj,
    })
