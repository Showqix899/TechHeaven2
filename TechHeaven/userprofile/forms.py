from django import forms
from .models import CustomUserProfile, UserAddress


class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUserProfile
        fields = ['phone_number', 'bio', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write something about yourself...'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            
        
        }


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'address_line1', 'address_line2', 'city', 
            'state', 'postal_code', 'country', 'is_default'
        ]
        widgets = {
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address, P.O. box'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, unit, building, floor, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State / Province / Region'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # We expect the request user to be passed in views like:
        # form = UserAddressForm(request.POST, user=request.user)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Only check limit on creation (not when updating an existing address)
        if not self.instance.pk and self.user:
            existing_count = UserAddress.objects.filter(profile__user=self.user).count()
            if existing_count >= 3:
                raise forms.ValidationError("You can only have up to 3 addresses.")
        
        return cleaned_data

        
