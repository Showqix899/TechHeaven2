from django.forms import ModelForm
from .models import Product
from django.forms import Textarea
from django import forms
from .models import Product,Category, Color, Brand


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'brand_name', 'price', 'stock',
            'discount', 'image', 'category', 'colors'
        ]
        widgets = {
            'description': Textarea(attrs={'rows': 4, 'cols': 40})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount and discount < 0:
            raise forms.ValidationError("Discount cannot be negative.")
        if discount and discount > 100:
            raise forms.ValidationError("Discount cannot exceed 100%.")
        return discount

    def save(self, commit=True):
        product = super().save(commit=False)

        # If discount applied
        if product.discount and product.discount > 0:
            # Store old price only if this is a new discount
            if not product.prev_price or product.prev_price == product.price:
                product.prev_price = product.price

            # Calculate discounted price
            product.price = product.prev_price - (
                product.prev_price * (product.discount / 100)
            )
        else:
            # If discount removed, restore original price
            if product.prev_price:
                product.price = product.prev_price
                product.prev_price = None

        if commit:
            product.save()
            self.save_m2m()

        return product



class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

class ColorForm(ModelForm):
    class Meta:
        model = Color
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

class BrandForm(ModelForm):

    class Meta:
        model = Brand
        fields=['brand_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

