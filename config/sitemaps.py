from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products_app.models import Product, Category
from blog_app.models import BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'
    
    def items(self):
        return ['products:home', 'products:product_list', 'products:bulk_order', 'products:contact']
    
    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return Product.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.created_at

class CategorySitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.created_at

class BlogSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'
    
    def items(self):
        return BlogPost.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.created_at