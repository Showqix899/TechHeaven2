from django.db import models
import uuid
from order.models import Order
from django.contrib.auth import get_user_model
# Create your models here.
User=get_user_model()

class PaymentHistory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    payment_method=models.CharField(max_length=30,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status=models.CharField(max_length=30,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)




