from django.contrib import admin
from .models import Product, ARModel, BodyMeasurement, ARSession, ARTryOnResult

@admin.register(ARModel)
class ARModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['product__name']

@admin.register(BodyMeasurement)
class BodyMeasurementAdmin(admin.ModelAdmin):
    list_display = ['user', 'height', 'chest', 'waist', 'updated_at']
    search_fields = ['user__username']

@admin.register(ARSession)
class ARSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'fit_rating', 'created_at']
    list_filter = ['fit_rating', 'created_at']
    search_fields = ['user__username', 'product__name']

@admin.register(ARTryOnResult)
class ARTryOnResultAdmin(admin.ModelAdmin):
    list_display = ['session', 'fit_score', 'size_recommendation', 'created_at']
    list_filter = ['fit_score', 'size_recommendation']
