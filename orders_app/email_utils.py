"""
Email utility functions for Marble Gallery
"""
from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation(order):
    """
    Send order confirmation email to customer
    """
    subject = f'Order Confirmation - #{order.order_number}'
    
    # Get customer name safely
    customer_name = order.user.get_full_name() if order.user.get_full_name() else order.user.username
    
    # Build email content
    message = f"""
    ═══════════════════════════════════════════════════════════
                        MARBLE GALLERY
                    ORDER CONFIRMATION
    ═══════════════════════════════════════════════════════════
    
    Dear {customer_name},
    
    Thank you for shopping with Marble Gallery!
    
    ───────────────────────────────────────────────────────────
    ORDER DETAILS
    ───────────────────────────────────────────────────────────
    Order Number:   {order.order_number}
    Order Date:     {order.created_at.strftime('%B %d, %Y at %I:%M %p')}
    Payment Method: {order.payment_method.upper()}
    Order Status:   {order.order_status.upper()}
    
    ───────────────────────────────────────────────────────────
    ORDER ITEMS
    ───────────────────────────────────────────────────────────
    """
    
    for item in order.items.all():
        message += f"""
    {item.product.name_en}
        Quantity: {item.quantity} sq.ft
        Price:    PKR {item.price_at_time}/sq.ft
        Total:    PKR {item.total_price}
    """
    
    message += f"""
    ───────────────────────────────────────────────────────────
    PAYMENT SUMMARY
    ───────────────────────────────────────────────────────────
    Subtotal:      PKR {order.subtotal}
    Shipping Cost: PKR {order.shipping_cost}
    Discount:      PKR {order.discount}
    ───────────────────────────────────────────────────────────
    TOTAL:         PKR {order.total}
    ───────────────────────────────────────────────────────────
    
    ───────────────────────────────────────────────────────────
    SHIPPING INFORMATION
    ───────────────────────────────────────────────────────────
    Your order will be shipped within 24-48 hours.
    
    Track your order: http://127.0.0.1:8000/orders/track/?order_number={order.order_number}
    
    ───────────────────────────────────────────────────────────
    NEED HELP?
    ───────────────────────────────────────────────────────────
    Contact us at: marblegallery2004@gmail.com
    Call us: +92 315 8510208
    
    Thank you for choosing Marble Gallery!
    
    Regards,
    Marble Gallery Team
    ═══════════════════════════════════════════════════════════
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        print(f"✅ Order confirmation email sent to {order.user.email} for order #{order.order_number}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_order_status_update(order, new_status, old_status=None):
    """
    Send order status update email to customer
    """
    subject = f'Order Status Update - #{order.order_number}'
    
    # Get customer name safely
    customer_name = order.user.get_full_name() if order.user.get_full_name() else order.user.username
    
    status_messages = {
        'confirmed': '✅ Your order has been confirmed and is being processed.',
        'processing': '🔄 Your order is now being processed and prepared for shipment.',
        'shipped': '📦 Great news! Your order has been shipped.',
        'out_for_delivery': '🚚 Your order is out for delivery today!',
        'delivered': '🏠 Your order has been delivered. Thank you for shopping with us!',
        'cancelled': '❌ Your order has been cancelled as requested.',
        'pending': '⏳ Your order is pending confirmation.',
    }
    
    status_text = status_messages.get(new_status, 'Your order status has been updated.')
    
    message = f"""
    ═══════════════════════════════════════════════════════════
                        MARBLE GALLERY
                    ORDER STATUS UPDATE
    ═══════════════════════════════════════════════════════════
    
    Dear {customer_name},
    
    Your order #{order.order_number} status has been updated:
    
    ┌─────────────────────────────────────────────────────────┐
    │  NEW STATUS: {new_status.upper()}                    │
    └─────────────────────────────────────────────────────────┘
    
    {status_text}
    
    """
    
    if old_status:
        message += f"""
    Previous Status: {old_status.upper()}
    
    """
    
    if order.tracking_number:
        message += f"""
    📦 TRACKING INFORMATION:
    Tracking Number: {order.tracking_number}
    
    Track your shipment at: https://www.tcs.com.pk/tracking/{order.tracking_number}
    """
    
    message += f"""
    
    ───────────────────────────────────────────────────────────
    ORDER SUMMARY
    ───────────────────────────────────────────────────────────
    Order Total: PKR {order.total}
    
    Track your order: http://127.0.0.1:8000/orders/track/?order_number={order.order_number}
    
    ───────────────────────────────────────────────────────────
    
    Thank you for shopping with Marble Gallery!
    
    Regards,
    Marble Gallery Team
    ═══════════════════════════════════════════════════════════
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        print(f"✅ Status update email sent for order #{order.order_number} to {order.user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send status email: {e}")
        return False


def send_welcome_email(user):
    """
    Send welcome email to new registered user
    """
    subject = 'Welcome to Marble Gallery!'
    
    # Get user name safely
    user_name = user.get_full_name() if user.get_full_name() else user.username
    
    message = f"""
    ═══════════════════════════════════════════════════════════
                        MARBLE GALLERY
                    WELCOME TO OUR FAMILY!
    ═══════════════════════════════════════════════════════════
    
    Dear {user_name},
    
    Welcome to Marble Gallery - Pakistan's premier online marble store!
    
    ───────────────────────────────────────────────────────────
    WHAT YOU CAN DO WITH YOUR ACCOUNT:
    ───────────────────────────────────────────────────────────
    ✓ Browse our premium marble collection
    ✓ Track your orders in real-time
    ✓ Request bulk quotes for projects
    ✓ Save your favorite products
    ✓ Get exclusive offers and discounts
    
    ───────────────────────────────────────────────────────────
    GET STARTED:
    ───────────────────────────────────────────────────────────
    Shop now: http://127.0.0.1:8000/products/
    Explore marble guides: http://127.0.0.1:8000/blog/
    
    Need bulk order? Visit: http://127.0.0.1:8000/bulk-order/
    
    ───────────────────────────────────────────────────────────
    
    Have questions? Contact our support team at marblegallery2004@gmail.com
    
    Happy Shopping!
    
    Regards,
    Marble Gallery Team
    ═══════════════════════════════════════════════════════════
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"✅ Welcome email sent to {user.email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")
        return False


def send_contact_confirmation(user_email, name, subject, message_content):
    """
    Send confirmation email when user submits contact form
    """
    subject = f'Thank you for contacting Marble Gallery'
    
    message = f"""
    ═══════════════════════════════════════════════════════════
                        MARBLE GALLERY
                    THANK YOU FOR CONTACTING US
    ═══════════════════════════════════════════════════════════
    
    Dear {name},
    
    Thank you for reaching out to us!
    
    We have received your message and will respond within 24 hours.
    
    ───────────────────────────────────────────────────────────
    YOUR MESSAGE:
    ───────────────────────────────────────────────────────────
    Subject: {subject}
    
    {message_content}
    
    ───────────────────────────────────────────────────────────
    
    If you need immediate assistance, please call us at +92 315 8510208
    
    Regards,
    Marble Gallery Team
    ═══════════════════════════════════════════════════════════
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        print(f"✅ Contact confirmation email sent to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send contact confirmation: {e}")
        return False