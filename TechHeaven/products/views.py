from django.shortcuts import render,redirect
from .models import Product, Category, Color,Brand
from .forms import ProductForm, CategoryForm, ColorForm,BrandForm
from django.db.models import Q
from accounts.decorators import admin_required
from django.http import HttpResponse
from cart.forms import AddToCartForm
from django.core.cache import cache
from .models import Brand
from .tasks import product_cache_update
from django.core.paginator import Paginator
from django.http import JsonResponse
from review.models import ProductReview
from django.db.models import Avg, Count




# Create your views here.

#product list view
def product_list(request):
    categories = cache.get('categories')
    brands = cache.get('brands')

    if not categories:
        categories = Category.objects.all()
        cache.set('categories', categories, timeout=60*5)  # cache for 5 minutes

    if not brands:
        brands = Brand.objects.all()
        cache.set('brands', brands, timeout=60*5)

    selected_category = request.GET.get('category')
    selected_brand = request.GET.get('brand')

    # Cache products with filter parameters as key
    cache_key = f"products_{selected_category}_{selected_brand}"
    products = cache.get(cache_key)

    if not products:
        products = Product.objects.all().order_by('-created_at')
        if selected_category:
            products = products.filter(category_id=selected_category)
        if selected_brand:
            products = products.filter(brand_name_id=selected_brand)
        cache.set(cache_key, products, timeout=60*2)  # cache for 2 minutes
    
    
    products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),  # Average of all related reviews' ratings
        total_reviews=Count('reviews')      # Total number of related reviews
    )

    paginator = Paginator(products, 8)  # 5 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'paginator': paginator,
        'page_obj': page_obj
    })

#product search view
def product_search(request):

    query = request.GET.get('q', '').strip()

    if query:  # Only search if query is not empty
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).order_by('-created_at')
        

        # Debugging output
        print("Query:", query)
        print("Matched products:", products)

    else:
        products = Product.objects.none()  # Return empty result set if query is blank

    if not products.exists():
        return render(request, 'accounts/error_message.html', {
            'message': f'No products found matching "{query}".'
        })

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query
    })

# product detail view
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        add_to_cart_form = AddToCartForm(initial={'quantity': 1})  # Initialize form with default quantity


        product_reviews = ProductReview.objects.filter(product=product).order_by('-created_at')

        
        
        return render(request, 'products/product_detail.html', {'product': product, 'add_to_cart_form': add_to_cart_form, 'product_reviews': product_reviews})
    except Product.DoesNotExist:
        return render(request, 'products/product_detail.html', {'error': 'Product not found.'})
    

# product create view
@admin_required
def product_create(request):
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)

            # Set prev_price from cleaned_data if exists
            prev_price = form.cleaned_data.get('prev_price')
            if prev_price:
                product.prev_price = prev_price

            product.save()
            form.save_m2m()  # Save ManyToMany like colors
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_create.html', {'form': form})




# product update view
@admin_required
def product_update(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return render(request, 'products/product_update.html', {'error': 'Product not found.'})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()  # The form handles all price/discount logic
            product_cache_update.delay()
            return render(request, 'products/product_update.html', {
                'form': ProductForm(instance=product),
                'success': 'Product updated successfully!'
            })
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_update.html', {'form': form})



# product delete view
@admin_required
def product_delete(request, product_id):
    
    try:
        product = Product.objects.get(id=product_id)
        if request.method == 'POST':
            product.delete()
            return render(request, 'products/product_delete.html', {'success': 'Product deleted successfully!'})
        return render(request, 'products/product_delete.html', {'product': product})
    except Product.DoesNotExist:
        return render(request, 'products/product_delete.html', {'error': 'Product not found.'})



#category add from
@admin_required
def category_add(request):
    
    message = None
    if request.method == 'POST':

        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            message = 'Category added successfully!'
        
        form = CategoryForm()  # Reset the form after saving
        return render(request, 'products/category_add.html', {'form': form, 'message': message})
    else:
        form = CategoryForm()
    return render(request, 'products/category_add.html', {'form': form, 'message': message})


# color add form
@admin_required
def color_add(request):
    
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()

        form = ColorForm()  # Reset the form after saving
        return render(request, 'products/color_add.html', {'form': form, 'message':'Color added successfully!'})
    else:
        form = ColorForm()
    return render(request, 'products/color_add.html', {'form': form})


#category and color list view
@admin_required
def list_categories_and_colors(request):
    
    categories = Category.objects.all()
    colors = Color.objects.all()
    brands=Brand.objects.all()

    return render(request, 'products/list.html', {'categories': categories, 'colors': colors,'brands':brands})

# Delete category view
@admin_required
def delete_category(request, category_id):
    
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return redirect("list_categories_and_colors")
        except Category.DoesNotExist:
            return HttpResponse('Category not found', status=404)
    return HttpResponse('Invalid method', status=405)


# Delete color view
@admin_required
def delete_color(request, color_id):
    
    if request.method == 'POST':
        try:
            color = Color.objects.get(id=color_id)
            color.delete()
            return redirect("list_categories_and_colors")
        except Color.DoesNotExist:
            return HttpResponse('Color not found', status=404)
    return HttpResponse('Invalid method', status=405)




#create brand
def add_brand(request):
    
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()

        form = BrandForm()  # Reset the form after saving
        return render(request, 'products/brand_add.html', {'form': form, 'message':'Brand added successfully!'})
    else:
        form = BrandForm()
    return render(request, 'products/brand_add.html', {'form': form})



# Delete brand view
@admin_required
def delete_brand(request, brand_id):
    
    if request.method == 'POST':
        try:
            brand = Brand.objects.get(id=brand_id)
            brand.delete()
            return redirect("list_categories_and_colors")
        except Brand.DoesNotExist:
            return HttpResponse('Brand not found', status=404)
    return HttpResponse('Invalid method', status=405)



def filter_product(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()

    selected_category = request.GET.get('category')
    selected_brand = request.GET.get('brand')


    if selected_category:
        products = products.filter(category_id=selected_category)

    if selected_brand:
        products = products.filter(brand_name_id=selected_brand)

    return render(request, 'products/product_list.html', {
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
    })