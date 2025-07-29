from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.ClothingUploadView.as_view(), name='upload'),
    path('<int:category_id>/', views.ClothingUploadView.as_view(), name='upload'),
    path('get-suggestions/', views.GetSuggestionsView.as_view(), name='get_suggestions'),   
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('add-to-wardrobe/<int:product_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),
    path('wardrobe/',views.wardrobe, name='wardrobe'),
    path('try-on/<int:product_id>/', views.try_on, name='try_on'),
    path('remove-from-wardrobe/<int:product_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
    path('ai-suggestions/<int:category_id>/', views.ai_suggestions, name='ai_suggestions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
