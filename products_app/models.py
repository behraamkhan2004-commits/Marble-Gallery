from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name_en = models.CharField(max_length=100)
    name_ur = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name_en
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


class Product(models.Model):
    FINISH_CHOICES = (
        ('polished', 'Polished'),
        ('honed', 'Honed'),
        ('leather', 'Leather'),
        ('brushed', 'Brushed'),
    )
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name_en = models.CharField(max_length=200)
    name_ur = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description_en = models.TextField()
    description_ur = models.TextField(blank=True)
    color = models.CharField(max_length=100)
    thickness = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    finish = models.CharField(max_length=20, choices=FINISH_CHOICES, default='polished')
    origin = models.CharField(max_length=100)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    main_image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name_en} - {self.sku}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price_per_sqft


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image for {self.product.name_en}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users_app.CustomUser', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name_en} - {self.rating}★"


class Wishlist(models.Model):
    user = models.ForeignKey('users_app.CustomUser', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name_en}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"
    
    class Meta:
        ordering = ['-created_at']


class BulkOrder(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    marble_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    delivery_city = models.CharField(max_length=100)
    address = models.TextField()
    requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.company_name} - {self.quantity} sq.ft"
    
    class Meta:
        ordering = ['-created_at']


class StockAlert(models.Model):
    user = models.ForeignKey('users_app.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name_en}"


class Comparison(models.Model):
    user = models.ForeignKey('users_app.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comparison - {self.id}"