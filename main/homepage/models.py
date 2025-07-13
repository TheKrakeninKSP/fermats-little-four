from django.db import models

from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')

    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Auto-generate slug on save
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"


class WardrobeItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user','category')

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_body_image = models.ImageField(upload_to='user_bodies/', null=True, blank=True)

    def __str__(self):
        return self.user.username
        verbose_name_plural = "Products"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/') # Requires Pillow to be installed
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    num_reviews = models.IntegerField(default=0)
    has_w_plus_shipping = models.BooleanField(default=False)
    shipping_days = models.IntegerField(null=True, blank=True)
    options_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # For items with price range

    def _str_(self):
        return self.name

    class Meta:
