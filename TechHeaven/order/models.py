from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from cart.models import CartItem, Cart  # Adjust as needed

import uuid
from products.models import Product



#order
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_item=models.ForeignKey(CartItem, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending')
    order_type = models.CharField(max_length=20,default='single',null=True,blank=True) # 'single' for single item order, 'multiple' for multiple items order
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method=models.CharField(max_length=100, null=True, blank=True,choices=[
       ('SSL Commerz', 'SSL Commerz'),
       ('Stripe', 'Stripe'),
    ])
    payment_id = models.CharField(max_length=100, blank=True, null=True) 
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):

        return f"Order {self.id} by {self.user.username} - Status: {self.status} - Total: ${self.total_amount:.2f}"
    



#order item

class OrderItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def total_price(self):
        return self.quantity * self.price_at_order