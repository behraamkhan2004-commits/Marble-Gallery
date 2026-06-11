from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart_app.cart import Cart
from delivery_app.models import ShippingRate
from .models import Order, OrderItem
from .email_utils import send_order_confirmation

@login_required
def order_create(request):
    cart = Cart(request)
    cities = ShippingRate.objects.all()
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile_number = request.POST.get('mobile_number')
        cnic = request.POST.get('cnic')
        city = request.POST.get('city')
        district = request.POST.get('district')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        
        # Get shipping cost based on selected city
        try:
            shipping_rate = ShippingRate.objects.get(city=city)
            shipping_cost = shipping_rate.cost
        except ShippingRate.DoesNotExist:
            shipping_cost = 200
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=cart.get_total_price(),
            shipping_cost=shipping_cost,
            total=cart.get_total_price() + shipping_cost,
            payment_method=payment_method,
            order_status='pending'
        )
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price_at_time=item['price']
            )
        
        # Clear cart
        cart.clear()
        
        # Send email confirmation to customer
        send_order_confirmation(order)
        
        messages.success(request, f'Order #{order.order_number} created successfully! A confirmation email has been sent to your email address.')
        return redirect('payments:payment_page', order_id=order.id)
    
    context = {
        'cart': cart,
        'cities': cities,
    }
    return render(request, 'orders_app/order_create.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders_app/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders_app/order_detail.html', {'order': order})


def track_order_page(request):
    order_number = request.GET.get('order_number')
    order = None
    progress_percentage = 0
    current_status_index = 0
    
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            status_sequence = ['pending', 'confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']
            if order.order_status in status_sequence:
                current_status_index = status_sequence.index(order.order_status)
            total_statuses = len(status_sequence) - 1
            progress_percentage = (current_status_index / total_statuses) * 100 if total_statuses > 0 else 0
        except Order.DoesNotExist:
            pass
    
    context = {
        'order': order,
        'progress_percentage': progress_percentage,
        'current_status_index': current_status_index,
    }
    return render(request, 'orders_app/track_order.html', context)


def download_invoice(request, order_id):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from django.http import HttpResponse
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 50, "MARBLE GALLERY")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, "Peshawar, Pakistan")
    p.drawString(50, height - 85, "Phone: +92 315 8510208")
    p.drawString(50, height - 100, "Email: marblegallery2004@gmail.com")
    
    # Invoice Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 140, f"INVOICE #{order.order_number}")
    
    # Order Details
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 170, f"Date: {order.created_at.strftime('%B %d, %Y')}")
    p.drawString(50, height - 185, f"Customer: {order.user.username}")
    p.drawString(50, height - 200, f"Payment Method: {order.payment_method.upper()}")
    
    # Table Header
    y = height - 250
    p.drawString(50, y, "Product")
    p.drawString(250, y, "Qty")
    p.drawString(350, y, "Price")
    p.drawString(450, y, "Total")
    
    # Table Items
    y -= 25
    for item in order.items.all():
        p.drawString(50, y, item.product.name_en[:30])
        p.drawString(250, y, str(item.quantity))
        p.drawString(350, y, f"PKR {item.price_at_time}")
        p.drawString(450, y, f"PKR {item.total_price}")
        y -= 20
    
    # Total
    y -= 20
    p.drawString(350, y, "TOTAL:")
    p.drawString(450, y, f"PKR {order.total}")
    
    p.showPage()
    p.save()
    
    return response
from django.http import JsonResponse
import json

def apply_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            
            from .models import Coupon
            from django.utils import timezone
            
            try:
                coupon = Coupon.objects.get(code=code, active=True)
                
                # Check if coupon is valid
                now = timezone.now()
                if coupon.valid_from <= now <= coupon.valid_to:
                    # Get cart total from session or cart
                    from cart_app.cart import Cart
                    cart = Cart(request)
                    cart_total = cart.get_total_price()
                    
                    # Check minimum amount
                    if cart_total >= coupon.minimum_amount:
                        # Store coupon in session
                        request.session['coupon_code'] = code
                        request.session['coupon_discount'] = coupon.discount_percent
                        
                        return JsonResponse({
                            'success': True, 
                            'message': f'Coupon applied! {coupon.discount_percent}% off'
                        })
                    else:
                        return JsonResponse({
                            'success': False, 
                            'message': f'Minimum order amount of PKR {coupon.minimum_amount} required'
                        })
                else:
                    return JsonResponse({'success': False, 'message': 'Coupon has expired'})
                    
            except Coupon.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})