from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name

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