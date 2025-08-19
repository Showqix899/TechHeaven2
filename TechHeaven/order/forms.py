from django import forms
from userprofile.models import UserAddress

class OrderAddressForm(forms.Form):
    existing_address = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Select an existing address",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_address_line1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
    )
    new_address_line2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'})
    )
    new_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    new_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'})
    )
    new_postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'})
    )
    new_country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['existing_address'].queryset = UserAddress.objects.filter(profile__user=user)

    def clean(self):
        cleaned_data = super().clean()
        existing = cleaned_data.get('existing_address')

        # Check if neither existing address selected nor new address fields filled
        new_address_fields = [
            cleaned_data.get('new_address_line1'),
            cleaned_data.get('new_city'),
            cleaned_data.get('new_state'),
            cleaned_data.get('new_postal_code'),
            cleaned_data.get('new_country'),
        ]

        if not existing and not all(new_address_fields[:1]):
            raise forms.ValidationError("Please select an existing address or fill in the new address line 1 at minimum.")

        # If existing address selected, ignore new address fields
        # If new address partially filled, check for all required fields
        if not existing:
            missing_fields = [field for field in ['new_city', 'new_state', 'new_postal_code', 'new_country'] if not cleaned_data.get(field)]
            if missing_fields:
                raise forms.ValidationError("Please fill in all required fields for the new address.")

        return cleaned_data
