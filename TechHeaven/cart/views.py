from django.shortcuts import render

from .models import Cart, CartItem
from products.models import Product
from .forms import AddToCartForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from django.core import cache

# Create your views here.


#get cart 
def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    return cart

#add to cart
@login_required
def add_to_cart(request,product_id):

    if not request.user.is_authenticated:
        return redirect('login')
    
    
    
    
    
    product=get_object_or_404(Product, id=product_id)

    form = AddToCartForm(request.POST)

    if form.is_valid():

        quantity = form.cleaned_data['quantity']
        cart = get_cart(request)
        item,created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
        )

        if created:
            item.quantity=quantity
        else:
            item.quantity += quantity

        item.save()

        message = f"{product.name} has been added to your cart."

        return render(request, 'products/product_detail.html', {
            'message': message,
            'product': product,
            'add_to_cart_form': AddToCartForm(initial={'quantity': 1})
        })
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'add_to_cart_form': form,
        'message': 'Invalid quantity'
    })

#remove cart item
@login_required
def remove_cart_item(request, item_id):

    if not request.user.is_authenticated:
        return redirect('login')
    
    try:

        item = CartItem.objects.get(id=item_id)

        item.delete()
        print(f"Item {item_id} removed from cart.")
        return redirect('view_cart')
    
    except CartItem.DoesNotExist:
        print(f"Item {item_id} does not exist in the cart.")
        return redirect('view_cart')


#view cart
@login_required
def view_cart(request):
    cart = get_cart(request)

    return render(request, 'carts/view_cart.html', {
        'cart': cart,
    })

#toggle item selection
@login_required
def toggle_item_selection(request,item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':

        if item.is_selected == False:
            item.is_selected = True
            item.save()
        else:
            item.is_selected=False
            item.save()
    
    return redirect('view_cart')


@login_required
def all_item_selection(request):
    cart=get_cart(request)
    items = CartItem.objects.filter(cart=cart,cart__user=request.user)
    if items.filter(is_selected=False).exists():

        items.update(is_selected=True)
    else:
        items.update(is_selected=False)

    return redirect('view_cart')

        
    
#update cart item
@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
            if quantity > 0:
                item.quantity = quantity
                item.save()
        except (TypeError, ValueError):
            pass  # Ignore invalid input
    return redirect('view_cart')