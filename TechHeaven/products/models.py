from django.db import models
import uuid

# Create your models here.
# product model
class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name= models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name or "unamed category"
    

class Color(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name or "unamed color"
    
class Brand(models.Model):

    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    brand_name=models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.brand_name or "unamed brand"

class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    brand_name=models.ForeignKey(Brand,on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prev_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # For discounted price
    stock = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # For product images
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    colors = models.ManyToManyField(Color, blank=True, related_name='products')  # For product colors
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

  