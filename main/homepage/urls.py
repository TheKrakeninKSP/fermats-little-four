from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('add-to-wardrobe/<int:category_id>/', views.add_to_wardrobe, name='add_to_wardrobe'),
    path('wardrobe/',views.wardrobe, name='wardrobe'),
    path('try-on/<int:category_id>/', views.try_on, name='try_on'),
    path('remove-from-wardrobe/<int:category_id>/', views.remove_from_wardrobe, name='remove_from_wardrobe'),
]