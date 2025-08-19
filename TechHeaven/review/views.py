from django.shortcuts import render
from django.http import HttpResponse
from .models import ProductReview, Feedback
from products.models import Product
from .forms import ProductReviewForm, FeedbackForm
from django.contrib.auth.decorators import login_required


# Create your views here.



#post a product review
@login_required
def post_review(request, product_id):
    product = Product.objects.get(id=product_id)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return HttpResponse("Review posted successfully!")
    else:
        form = ProductReviewForm()

    return render(request, 'review/post_review.html', {'form': form, 'product': product})