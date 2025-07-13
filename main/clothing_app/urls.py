from django.urls import path
from . import views

app_name = 'clothing_app'

urlpatterns = [
    path('', views.ClothingUploadView.as_view(), name='upload'),
    path('get-suggestions/', views.GetSuggestionsView.as_view(), name='get_suggestions'),
]