from django.contrib import admin
from .models import ClothingUpload

@admin.register(ClothingUpload)
class ClothingUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'classified_type', 'classified_color', 'uploaded_at']
    list_filter = ['classified_type', 'classified_color', 'uploaded_at']
    readonly_fields = ['uploaded_at']