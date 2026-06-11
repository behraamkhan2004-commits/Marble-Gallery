from django.db import models

class ShippingRate(models.Model):
    city = models.CharField(max_length=100, unique=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(default=3)
    
    def __str__(self):
        return f"{self.city}: PKR {self.cost}"