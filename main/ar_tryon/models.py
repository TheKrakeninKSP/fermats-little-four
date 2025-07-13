from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid

class Product(models.Model):
    """Main product model - assuming you have this already"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ARModel(models.Model):
    """3D model data for AR visualization"""
    CATEGORY_CHOICES = [
        ('shirt', 'Shirt'),
        ('pants', 'Pants'),
        ('dress', 'Dress'),
        ('jacket', 'Jacket'),
        ('shoes', 'Shoes'),
        ('accessory', 'Accessory'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='ar_model')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # 3D model files
    model_file = models.FileField(
        upload_to='ar_models/',
        validators=[FileExtensionValidator(allowed_extensions=['glb', 'gltf', 'fbx'])]
    )
    texture_file = models.FileField(
        upload_to='ar_textures/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        null=True, blank=True
    )
    
    # Sizing and positioning data
    sizing_data = models.JSONField(default=dict, help_text="Size mapping and scaling factors")
    anchor_points = models.JSONField(default=dict, help_text="Body anchor points for positioning")
    
    # AR-specific metadata
    scale_factor = models.FloatField(default=1.0)
    rotation_offset = models.JSONField(default=dict, help_text="Default rotation adjustments")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AR Model for {self.product.name}"

class BodyMeasurement(models.Model):
    """User body measurements for better fitting"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='body_measurements')
    
    # Basic measurements (in cm)
    height = models.FloatField(null=True, blank=True)
    chest = models.FloatField(null=True, blank=True)
    waist = models.FloatField(null=True, blank=True)
    hips = models.FloatField(null=True, blank=True)
    shoulder_width = models.FloatField(null=True, blank=True)
    arm_length = models.FloatField(null=True, blank=True)
    inseam = models.FloatField(null=True, blank=True)
    
    # Preferred sizes
    shirt_size = models.CharField(max_length=10, blank=True)
    pants_size = models.CharField(max_length=10, blank=True)
    shoe_size = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Measurements for {self.user.username}"

class ARSession(models.Model):
    """Track AR try-on sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ar_sessions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Session data
    duration = models.DurationField(null=True, blank=True)
    interaction_data = models.JSONField(default=dict, help_text="User interactions during session")
    
    # Results
    fit_rating = models.IntegerField(null=True, blank=True, help_text="User's fit rating 1-5")
    feedback = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to='ar_screenshots/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AR Session - {self.user.username} - {self.product.name}"

class ARTryOnResult(models.Model):
    """Store try-on results and recommendations"""
    session = models.ForeignKey(ARSession, on_delete=models.CASCADE, related_name='results')
    
    # Fit analysis
    fit_score = models.FloatField(help_text="Calculated fit score 0-100")
    size_recommendation = models.CharField(max_length=20)
    fit_issues = models.JSONField(default=list, help_text="List of potential fit problems")
    
    # Visual analysis
    color_match_score = models.FloatField(null=True, blank=True)
    style_compatibility = models.FloatField(null=True, blank=True)
    
    # Recommendations
    recommended_products = models.ManyToManyField(Product, blank=True, related_name='recommended_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Try-on result for {self.session.product.name}"