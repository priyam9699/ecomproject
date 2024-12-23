from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('Wholeseller', 'Wholeseller'),
        ('Customer', 'Customer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=100, blank=True, null=True)  # Wholeseller
    address = models.TextField(blank=True, null=True)  # Wholeseller
    sell_on_amazon = models.BooleanField(default=False)  # Customer
    sell_on_flipkart = models.BooleanField(default=False)  # Customer
    sell_on_meesho = models.BooleanField(default=False)  # Customer

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Home & Kitchen', 'Home & Kitchen'),
        ('Health & PersonalCare', 'Health & PersonalCare'),
        ('Safety Products', 'Safety Products'),
        ('Electronic', 'Electronic'),
        ('Monsoon Collection', 'Monsoon Collection'),
        ('Baby Products', 'Baby Products'),
        ('Stationaries', 'Stationaries'),
        ('Home Decor', 'Home Decor'),
        ('Packaging Material', 'Packaging Material'),
    ]

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    hsn_code = models.CharField(max_length=20, null=True, blank=True)
    carton_quantity = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Electronics')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model


    def __str__(self):
        return self.name

class SearchLog(models.Model):
    query = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=1)  # Track how many times a query is searched

    def __str__(self):
        return self.query
