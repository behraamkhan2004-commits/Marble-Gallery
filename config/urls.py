"""
Main URL Configuration for Marble Gallery
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap, BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('products_app.urls')),
    path('users/', include('users_app.urls')),
    path('cart/', include('cart_app.urls')),
    path('orders/', include('orders_app.urls')),
    path('blog/', include('blog_app.urls')),
    path('payments/', include('payments_app.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)