from django.forms import ModelForm
from .models import ProductReview, Feedback
from django import forms
from django.core.validators import MaxLengthValidator


class ProductReviewForm(ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control',
                'placeholder': 'Enter rating (1-5)',
                'oninput': "if(this.value>5) this.value=5; if(this.value<1) this.value=1;"
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your review here...',
                'class': 'form-control'
            }),
        }

    def clean(self):
        rating = self.cleaned_data.get('rating')
        comment = self.cleaned_data.get('comment')

        if not rating or not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        if not comment or len(comment) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")

        return self.cleaned_data


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Your feedback is valuable to us!',
                'class': 'form-control'
            }),
        }
        labels = {
            'comment': 'Feedback Comment',
        }
        help_texts = {
            'comment': 'Please provide your feedback or suggestions.',
        }
        error_messages = {
            'comment': {
                'required': 'Feedback comment is required.',
                'max_length': 'Feedback comment cannot exceed 500 characters.',
            },
        }
        validators = [
            MaxLengthValidator(500, message="Feedback comment cannot exceed 500 characters.")
        ]
