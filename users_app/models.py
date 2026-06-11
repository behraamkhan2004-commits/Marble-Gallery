from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('contractor', 'Contractor'),
        ('builder', 'Builder'),
    )
    
    phone_number = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    company_name = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return self.username