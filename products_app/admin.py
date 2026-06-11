from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview, Wishlist, ContactMessage, BulkOrder

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name_en',)}
    list_editable = ('is_active',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'price_per_sqft', 'stock_quantity', 'is_featured', 'is_active')
    list_editable = ('price_per_sqft', 'stock_quantity', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_main')
    list_filter = ('is_main',)

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('rating', 'is_approved')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)

@admin.register(BulkOrder)
class BulkOrderAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'quantity', 'marble_type', 'created_at', 'is_read')
    list_filter = ('is_read', 'marble_type')
    search_fields = ('company_name', 'contact_person', 'email', 'phone')
    list_editable = ('is_read',)