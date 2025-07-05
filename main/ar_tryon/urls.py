from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ARTryOnViewSet, BodyMeasurementViewSet, ar_tryon_page

router = DefaultRouter()
router.register(r'ar-tryon', ARTryOnViewSet, basename='ar-tryon')
router.register(r'measurements', BodyMeasurementViewSet, basename='measurements')

urlpatterns = [
    path('api/', include(router.urls)),
    path('tryon/', ar_tryon_page, name='ar-tryon-page'),
]