from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
import uuid

User = get_user_model()
# Create your models here.


#cart
class Cart(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key= models.CharField(max_length=255, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):

        return sum(item.total_price() for item in self.items.all())
    



#cart items
class CartItem(models.Model):


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE , related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    is_selected = models.BooleanField(default=False,null=True,blank=True)  # To indicate if the item is selected for checkout
    quantity = models.PositiveBigIntegerField(default=1)
    status=models.CharField(max_length=100,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)




    def total_price(self):

        return self.quantity * self.product.price