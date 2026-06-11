from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products_app.models import Product
from .cart import Cart

def cart_detail(request):
    """Display shopping cart with coupon discount"""
    cart = Cart(request)
    
    # Get coupon info
    coupon_code = cart.get_coupon_code()
    discount_amount = cart.get_discount_amount()
    original_subtotal = cart.get_original_subtotal()
    total_after_discount = cart.get_total_price()
    
    context = {
        'cart': cart,
        'coupon_code': coupon_code,
        'discount_amount': discount_amount,
        'original_subtotal': original_subtotal,
        'total_after_discount': total_after_discount,
    }
    return render(request, 'cart_app/cart_detail.html', context)


@require_POST
def cart_add(request, product_id):
    """Add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock availability
    if quantity > product.stock_quantity:
        messages.error(request, f'Sorry, only {product.stock_quantity} units available.')
        return redirect('products:product_detail', product_slug=product.slug)
    
    cart.add(product=product, quantity=quantity, update_quantity=False)
    messages.success(request, f'{product.name_en} added to cart!')
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update cart item quantity"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        if quantity > product.stock_quantity:
            messages.error(request, f'Sorry, only {product.stock_quantity} units available.')
            return redirect('cart:cart_detail')
        cart.add(product=product, quantity=quantity, update_quantity=True)
        messages.success(request, 'Cart updated successfully.')
    else:
        cart.remove(product)
    
    return redirect('cart:cart_detail')


@require_POST
def apply_coupon(request):
    """Apply coupon to cart"""
    import json
    from django.utils import timezone
    from orders_app.models import Coupon
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'success': False, 'message': 'Please enter a coupon code'})
        
        try:
            coupon = Coupon.objects.get(code=code, active=True)
            now = timezone.now()
            
            if coupon.valid_from <= now <= coupon.valid_to:
                # Store coupon in session
                request.session['coupon_code'] = code
                request.session['coupon_discount'] = coupon.discount_percent
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Coupon applied! {coupon.discount_percent}% off'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Coupon has expired'})
                
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def remove_coupon(request):
    """Remove coupon from cart"""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    return JsonResponse({'success': True, 'message': 'Coupon removed'})