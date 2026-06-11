from django.db import models
from django.utils.text import slugify

class BlogPost(models.Model):
    CATEGORY_CHOICES = (
        ('design', 'Design Tips'),
        ('maintenance', 'Maintenance'),
        ('trends', 'Trends 2026'),
        ('guide', 'Buying Guide'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='guide')
    content = models.TextField()
    excerpt = models.TextField(max_length=300)
    image = models.ImageField(upload_to='blog/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)