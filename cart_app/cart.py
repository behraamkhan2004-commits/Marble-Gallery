"""
Shopping cart class for managing cart session
"""
from decimal import Decimal
from django.conf import settings
from products_app.models import Product

class Cart:
    """Shopping cart class to handle all cart operations"""
    
    def __init__(self, request):
        """Initialize the cart from session"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    
    def add(self, product, quantity=1, update_quantity=False):
        """Add a product to the cart or update its quantity"""
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.current_price),
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        """Mark session as modified to ensure it gets saved"""
        self.session.modified = True
    
    def remove(self, product):
        """Remove a product from the cart"""
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        """Iterate over the items in the cart and get products from database"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """Return total quantity of items in cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_original_subtotal(self):
        """Get original subtotal without discount"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Calculate total price of all items with coupon discount"""
        total = self.get_original_subtotal()
        
        # Apply coupon discount if exists
        discount_percent = self.session.get('coupon_discount', 0)
        if discount_percent > 0:
            discount_amount = total * Decimal(discount_percent) / 100
            total = total - discount_amount
        
        return total
    
    def get_discount_amount(self):
        """Get discount amount from applied coupon"""
        total = self.get_original_subtotal()
        discount_percent = self.session.get('coupon_discount', 0)
        if discount_percent > 0:
            return total * Decimal(discount_percent) / 100
        return Decimal(0)
    
    def get_coupon_code(self):
        """Get applied coupon code"""
        return self.session.get('coupon_code', None)
    
    def clear(self):
        """Remove cart from session"""
        del self.session[settings.CART_SESSION_ID]
        self.save()