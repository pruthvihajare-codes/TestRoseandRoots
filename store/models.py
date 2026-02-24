# models.py (in your app, e.g., cart/models.py or add to existing models)

from django.db import models
from django.conf import settings
from masters.models import Bouquet

class Cart(models.Model):
    """Shopping cart header model - pure table definition only"""
    id = models.AutoField(primary_key=True)
    
    # For guest users
    session_key = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    # For logged-in users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
        # One cart per session or per user
        constraints = [
            models.UniqueConstraint(fields=['session_key'], name='unique_session_cart'),
            models.UniqueConstraint(fields=['user'], name='unique_user_cart'),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email}"
        return f"Cart - {self.session_key}"

class CartItem(models.Model):
    """Shopping cart items - pure table definition only"""
    id = models.AutoField(primary_key=True)
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    bouquet = models.ForeignKey(
        Bouquet,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    
    # Store useful product information for quick reference
    bouquet_name = models.CharField(max_length=200, null=True, blank=True)
    bouquet_slug = models.SlugField(max_length=200, null=True, blank=True)
    bouquet_image = models.CharField(max_length=500, null=True, blank=True)
    
    # Store encrypted ID for URL safety
    encrypted_id = models.CharField(max_length=500, null=True, blank=True)
    
    # Price at time of adding
    price_at_add = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_item'
        unique_together = ['cart', 'bouquet']
    
    def __str__(self):
        return f"{self.bouquet_name or 'Product'} in cart"