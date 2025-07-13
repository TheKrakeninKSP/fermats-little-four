from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from .models import ClothingUpload
from .forms import ClothingUploadForm
from .services import ClothingClassifier, WalmartAPIService
import json

class ClothingUploadView(View):
    def get(self, request):
        form = ClothingUploadForm()
        return render(request, 'clothing_app/upload.html', {'form': form})
    
    def post(self, request):
        form = ClothingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save()
            
            # Store upload ID in session for later use
            request.session['current_upload_id'] = upload.id
            
            return render(request, 'clothing_app/upload.html', {
                'form': ClothingUploadForm(),
                'upload': upload,
                'show_classify_button': True
            })
        
        return render(request, 'clothing_app/upload.html', {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class GetSuggestionsView(View):
    def post(self, request):
        upload_id = request.session.get('current_upload_id')
        
        if not upload_id:
            return JsonResponse({'error': 'No upload found'}, status=400)
        
        try:
            upload = ClothingUpload.objects.get(id=upload_id)
            
            # Initialize services
            classifier = ClothingClassifier()
            walmart_service = WalmartAPIService()
            
            # Classify the clothing
            clothing_type, clothing_color = classifier.classify_clothing(upload.image.path)
            
            # Update the upload with classification results
            upload.classified_type = clothing_type
            upload.classified_color = clothing_color
            upload.save()
            
            # Get complementary items
            suggestions = walmart_service.get_complementary_items(clothing_type, clothing_color)
            
            return JsonResponse({
                'classified_type': clothing_type,
                'classified_color': clothing_color,
                'suggestions': suggestions
            })
            
        except ClothingUpload.DoesNotExist:
            return JsonResponse({'error': 'Upload not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)