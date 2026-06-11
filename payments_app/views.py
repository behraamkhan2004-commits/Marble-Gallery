from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders_app.models import Order

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments_app/payment_form.html', {
        'total': order.total,
        'order_id': order.id
    })

@login_required
def jazzcash_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # JazzCash integration - For demo, redirect to success
    return redirect('payments:payment_success', order_id=order_id)

@login_required
def easypaisa_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # EasyPaisa integration - For demo, redirect to success
    return redirect('payments:payment_success', order_id=order_id)

@login_required
def cod_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = 'pending'
    order.order_status = 'confirmed'
    order.save()
    messages.success(request, f'Order #{order.order_number} confirmed!')
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = 'paid'
    order.order_status = 'confirmed'
    order.save()
    return render(request, 'payments_app/payment_success.html', {
        'order_number': order.order_number,
        'order_id': order.id
    })

@login_required
def payment_failed(request, order_id):
    return render(request, 'payments_app/payment_failed.html', {
        'error_message': 'Payment failed. Please try again.',
        'order_id': order_id
    })