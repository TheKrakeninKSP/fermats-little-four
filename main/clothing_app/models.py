from django.db import models
from django.core.validators import FileExtensionValidator

class ClothingUpload(models.Model):
    image = models.ImageField(
        upload_to='clothing_images/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    classified_type = models.CharField(max_length=100, blank=True)
    classified_color = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Upload {self.id} - {self.classified_type} {self.classified_color}"