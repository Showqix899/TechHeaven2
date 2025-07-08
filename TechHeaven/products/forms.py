from django.forms import ModelForm
from .models import Product
from django.forms import Textarea
from django import forms
from .models import Product,Category, Color, Brand


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description','brand_name' ,'price', 'stock', 'discount', 'image', 'category','colors']
        widgets = {
            'description': Textarea(attrs={'rows': 4, 'cols': 40})
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })


    def clean(self):

        cleaned_data= super().clean()
        price = cleaned_data.get('price')
        discount = cleaned_data.get('discount')


        if discount and price:

            cleaned_data['prev_price'] = price

            discounted_price = price - (price * (discount / 100))

            if discounted_price < 0:
                raise forms.ValidationError("Discounted price cannot be negative.")
            
            cleaned_data['price'] = discounted_price


        return cleaned_data
    


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

