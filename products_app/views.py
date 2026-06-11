from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Category, Product, ProductReview, Wishlist, ContactMessage, BulkOrder
from .forms import ProductReviewForm
import json

def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_products = Product.objects.filter(is_new=True, is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'products_app/home.html', context)


def product_list(request, category_slug=None):
    products = Product.objects.filter(is_active=True)
    category = None
    page_title = "All Products"
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        page_title = category.name_en
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.strip():
        try:
            products = products.filter(price_per_sqft__gte=float(min_price))
        except:
            pass
    if max_price and max_price.strip():
        try:
            products = products.filter(price_per_sqft__lte=float(max_price))
        except:
            pass
    
    # Color filter
    color = request.GET.get('color')
    if color and color != 'all':
        products = products.filter(color=color)
    
    # Finish filter
    finish = request.GET.get('finish')
    if finish and finish != 'all':
        products = products.filter(finish=finish)
    
    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price_per_sqft')
    elif sort == 'price_high':
        products = products.order_by('-price_per_sqft')
    elif sort == 'name_asc':
        products = products.order_by('name_en')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_colors = Product.objects.filter(is_active=True).values_list('color', flat=True).distinct()
    all_finishes = Product.objects.filter(is_active=True).values_list('finish', flat=True).distinct()
    
    context = {
        'products': page_obj,
        'category': category,
        'page_title': page_title,
        'all_colors': all_colors,
        'all_finishes': all_finishes,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_color': color,
        'current_finish': finish,
        'current_sort': sort,
    }
    return render(request, 'products_app/product_list.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    product.views_count += 1
    product.save()
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    avg_rating = 0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    form = ProductReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted and will appear after approval.')
            return redirect('products:product_detail', product_slug=product.slug)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'form': form,
    }
    return render(request, 'products_app/product_detail.html', context)


def search(request):
    query = request.GET.get('q', '')
    products = []
    if query:
        products = Product.objects.filter(
            Q(name_en__icontains=query) |
            Q(name_ur__icontains=query) |
            Q(description_en__icontains=query),
            is_active=True
        )
    
    context = {
        'products': products,
        'query': query,
        'count': len(products),
    }
    return render(request, 'products_app/search.html', context)


def bulk_order(request):
    if request.method == 'POST':
        messages.success(request, 'Your bulk order request has been submitted! Our sales team will contact you within 24 hours.')
        return redirect('products:bulk_order')
    return render(request, 'products_app/bulk_order.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('products:contact')
    
    return render(request, 'products_app/contact.html')


def about(request):
    return render(request, 'products_app/about.html')


def gallery(request):
    products = Product.objects.filter(is_active=True)[:12]
    return render(request, 'products_app/gallery.html', {'products': products})


def quality(request):
    return render(request, 'products_app/quality.html')


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.name_en} added to wishlist!')
    else:
        messages.info(request, f'{product.name_en} is already in your wishlist.')
    return redirect('products:wishlist')


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products_app/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, 'Item removed from wishlist.')
    return redirect('products:wishlist')

#comaprison function
def comparison(request):
    """Display comparison page"""
    product_ids = []
    
    # Get product IDs from URL parameter
    ids_param = request.GET.get('ids')
    if ids_param:
        product_ids = ids_param.split(',')
        # Save to session for future use
        request.session['comparison_products'] = product_ids
    else:
        # Try to get from session
        product_ids = request.session.get('comparison_products', [])
    
    # Convert to integers and filter
    product_ids = [int(id) for id in product_ids if id.isdigit()]
    products = Product.objects.filter(id__in=product_ids, is_active=True) if product_ids else []
    
    context = {
        'products': products,
        'product_count': len(products),
    }
    return render(request, 'products_app/comparison.html', context)