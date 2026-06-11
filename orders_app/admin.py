from django.contrib import admin
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_time')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'order_status', 'payment_method', 'created_at')
    list_filter = ('order_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    list_editable = ('order_status',)
    readonly_fields = ('order_number', 'created_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'created_at')
        }),
        ('Order Status', {
            'fields': ('order_status', 'payment_method')
        }),
        ('Payment Summary', {
            'fields': ('subtotal', 'shipping_cost', 'total')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            try:
                original = Order.objects.get(pk=obj.pk)
                old_status = original.order_status
            except Order.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)
        
        # Send email if status changed
        if change and old_status and old_status != obj.order_status:
            from .email_utils import send_order_status_update
            send_order_status_update(obj, obj.order_status, old_status)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_time')
    search_fields = ('order__order_number', 'product__name_en')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_to', 'active')
    list_filter = ('active',)
    list_editable = ('discount_percent', 'active')