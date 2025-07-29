import os
import sys
import glob
import json
import base64
import requests
from io import BytesIO

from PIL import Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from openai import OpenAI

from homepage.models import Category, Product, Profile, WardrobeItem, ClothingUpload
from homepage.forms import ProfileImageForm, ClothingUploadForm
from homepage.services import ClothingClassifier, WalmartAPIService
from homepage.ai_clothing_pairer import suggest_pairs
from time import time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from PIL import Image
from io import BytesIO
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import os 
from time import time # Add this import statement!

# Assuming these imports are correct based on your project structure
from .models import Profile, Product, WardrobeItem 
from .forms import ProfileImageForm 

client = OpenAI(api_key="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")

def resize_image_to_512(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((512, 512))
    byte_io = BytesIO()
    img.save(byte_io, format="JPEG", quality=95)
    byte_io.seek(0)
    return byte_io


def home(request):
    categories = Category.objects.exclude(slug="uncategorized")
    context = {"categories": categories}
    return render(request, "home.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(
        request,
        "category_detail.html",
        {
            "category": category,
            "products": products,
            "page_title": f"{category.name} - Products",
        },
    )


def resize_image_to_512(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((512, 512))
    byte_io = BytesIO()
    img.save(byte_io, format="JPEG", quality=95)
    byte_io.seek(0)
    return byte_io


@login_required
def add_to_wardrobe(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WardrobeItem.objects.get_or_create(user=request.user, product=product)
    return redirect("home")  


from .forms import ProfileImageForm
from .models import Profile


@login_required
def wardrobe(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Store the old file
            old_image = None
            if profile.full_body_image:
                old_image = profile.full_body_image.path

            # Save the new one
            form.save()

            # Delete the old file if a new one was uploaded
            if "full_body_image" in request.FILES and old_image:
                import os

                if os.path.exists(old_image):
                    os.remove(old_image)

            return redirect("wardrobe")

    else:
        form = ProfileImageForm(instance=profile)

    items = WardrobeItem.objects.filter(user=request.user).select_related("product", "product__category")

    return render(request, "wardrobe.html", {"wardrobe_items": items, "form": form})


@login_required
def remove_from_wardrobe(request, category_id):
    item = get_object_or_404(WardrobeItem, user=request.user, category_id=category_id)
    item.delete()
    return redirect("wardrobe")

"""@login_required
def try_on(request, product_id):
    profile = get_object_or_404(Profile, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if not profile.full_body_image:
        messages.error(request, "Please upload your full-body image first.")
        return redirect("wardrobe")

    # Get file paths
    avatar_path = profile.full_body_image.path
    cloth_path = product.image.path

    # Load images and concatenate vertically
    avatar = Image.open(avatar_path).convert("RGBA")
    cloth = Image.open(cloth_path).convert("RGBA")
    
    # Resize cloth to match avatar width
    cloth = cloth.resize((avatar.width, int(cloth.height * (avatar.width / cloth.width))))
    
    # Concatenate
    combined_height = avatar.height + cloth.height
    concat_img = Image.new("RGBA", (avatar.width, combined_height), (255, 255, 255, 0))
    concat_img.paste(avatar, (0, 0))
    concat_img.paste(cloth, (0, avatar.height))

    # Save temporarily
    concat_io = BytesIO()
    concat_img.save(concat_io, format="PNG")
    concat_io.seek(0)

    # Send to OpenAI GPT-image-1
    prompt = 
    response = client.images.edit(
        model="gpt-image-1",
        image=[("concat.png", concat_io)],
        prompt=prompt
    )

    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    # Save the result
    result_path = f"tryon_results/{request.user.username}_{product.id}.png"
    saved_path = default_storage.save(result_path, ContentFile(image_bytes))
    result_url = settings.MEDIA_URL + result_path

    form = ProfileImageForm(instance=profile)
    items = WardrobeItem.objects.filter(user=request.user).select_related("product")

    from time import time
    return render(
        request,
        "wardrobe.html",
        {
            "wardrobe_items": items,
            "form": form,
            "result_url": result_url,
            "tried_on": product.name,
            "timestamp": int(time()),
        },
    )"""

@login_required
def try_on(request, product_id):
    profile = get_object_or_404(Profile, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    if not profile.full_body_image:
        messages.error(request, "Please upload your full-body image first.")
        return redirect("wardrobe")

    # --- Start of Modified Logic ---
    # Determine the base image for the try-on operation
    # Check if a 'last_try_on_image' URL exists in the session
    # and if the file actually exists on the filesystem.
    last_try_on_url = request.session.get('last_try_on_url')
    
    if last_try_on_url:
        # Convert MEDIA_URL relative path to an absolute file path
        # This assumes your MEDIA_ROOT is correctly configured and accessible
        last_try_on_path = os.path.join(settings.MEDIA_ROOT, last_try_on_url.replace(settings.MEDIA_URL, ''))
        
        if os.path.exists(last_try_on_path):
            avatar_path = last_try_on_path
        else:
            # Fallback to original full_body_image if the session path is invalid
            avatar_path = profile.full_body_image.path
            # Clear invalid session entry
            request.session.pop('last_try_on_url', None) 
    else:
        avatar_path = profile.full_body_image.path
    # --- End of Modified Logic ---
        
    cloth_path = product.image.path

    try:
        # Load images and concatenate vertically
        avatar = Image.open(avatar_path).convert("RGBA")
        cloth = Image.open(cloth_path).convert("RGBA")
        
        # Resize cloth to match avatar width (maintain aspect ratio)
        cloth = cloth.resize((avatar.width, int(cloth.height * (avatar.width / cloth.width))))
        
        # Concatenate
        combined_height = avatar.height + cloth.height
        concat_img = Image.new("RGBA", (avatar.width, combined_height), (255, 255, 255, 0))
        concat_img.paste(avatar, (0, 0))
        concat_img.paste(cloth, (0, avatar.height))

        # Save temporarily to BytesIO
        concat_io = BytesIO()
        concat_img.save(concat_io, format="PNG")
        concat_io.seek(0)

        # Send to OpenAI GPT-image-1 with an updated, more generic prompt
        prompt = f"""
        In this image, there are two elements vertically arranged: a human and a piece of clothing (specifically a {product.name}).
        Please generate a realistic image where the human is wearing the {product.name}.
        The human should retain any clothing already present in the upper part of the first image and wear the new item on top or in addition to existing attire if appropriate for the item type.
        """
        response = client.images.edit(
            model="gpt-image-1",
            image=[("concat.png", concat_io)],
            prompt=prompt,
            n=1, 
            size="1024x1024" 
        )

        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        # Save the result image with a unique filename to avoid conflicts.
        # We'll use a generic name for demonstration, not user/product specific.
        result_filename = f"last_tryon_result_{int(time())}.png" 
        result_path = f"tryon_results/{result_filename}"
        saved_path_name = default_storage.save(result_path, ContentFile(image_bytes))
        result_url = settings.MEDIA_URL + saved_path_name

        # --- Start of Modified Logic ---
        # Store the URL of the newly generated image in the session
        request.session['last_try_on_url'] = result_url
        # --- End of Modified Logic ---

    except Exception as e:
        messages.error(request, f"Error trying on the item: {e}")
        result_url = None 
        # Clear any previous valid try-on from session on error
        request.session.pop('last_try_on_url', None)

    form = ProfileImageForm(instance=profile)
    items = WardrobeItem.objects.filter(user=request.user).select_related("product")

    return render(
        request,
        "wardrobe.html",
        {
            "wardrobe_items": items,
            "form": form,
            "result_url": result_url,
            "tried_on": product.name,
            "timestamp": int(time()), 
        },
    )
"""@login_required
def try_on(request, category_id):

    profile = get_object_or_404(Profile, user=request.user)
    category = get_object_or_404(Category, id=category_id)
    if not profile.full_body_image:
        messages.error(request, "Please upload your full-body image first.")
        return redirect("wardrobe")

    # Full paths
    avatar_path = default_storage.path(profile.full_body_image.name)
    cloth_path = default_storage.path(category.image.name)

    # Resize and prepare images
    avatar_io = resize_image_to_512(avatar_path)
    cloth_io = resize_image_to_512(cloth_path)

    headers = {
        "x-rapidapi-key": "91de88b5a5msh84a5edba908ba7bp14306djsnddd6c65aa846",
        "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com",
    }

    files = {
        "avatar_image": ("avatar.jpg", avatar_io, "image/jpeg"),
        "clothing_image": ("cloth.jpg", cloth_io, "image/jpeg"),
    }

    response = requests.post(
        "https://try-on-diffusion.p.rapidapi.com/try-on-file",
        headers=headers,
        files=files,
        data={"seed": "-1"},
    )

    if response.status_code == 200:
        result_path = f"tryon_results/{request.user.username}_{category.id}.jpg"
        full_path = default_storage.save(result_path, BytesIO(response.content))
        result_url = settings.MEDIA_URL + result_path
    else:
        result_url = None

    items = WardrobeItem.objects.filter(user=request.user).select_related("category")
    form = ProfileImageForm(instance=profile)

    from time import time

    return render(
        request,
        "wardrobe.html",
        {
            "wardrobe_items": items,
            "form": form,
            "result_url": result_url,
            "tried_on": category.name,
            "timestamp": int(time()),
        },
    )"""

@login_required
def ai_suggestions(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    image_path = category.image.path

    # Generate AI suggestions (this will create images in paired_outfits/)
    suggest_pairs(image_path)

    # Find the latest output directory for this clothing type
    import os
    from datetime import datetime

    # Get clothing type
    from .ai_clothing_pairer import OUTPUT_BASE_DIR, classify_clothing

    clothing_type = classify_clothing(image_path)
    type_dir = os.path.join(OUTPUT_BASE_DIR, clothing_type)
    # Find the latest timestamped folder
    subdirs = [
        os.path.join(type_dir, d)
        for d in os.listdir(type_dir)
        if os.path.isdir(os.path.join(type_dir, d))
    ]
    latest_dir = max(subdirs, key=os.path.getmtime)

    # List all generated images
    image_files = glob.glob(os.path.join(latest_dir, "*.png"))
    # Convert to media URLs
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    result_urls = [
        {
            "url": settings.MEDIA_URL + os.path.relpath(f, media_root),
            "name": os.path.splitext(os.path.basename(f))[0],
        }
        for f in image_files
    ]

    return render(
        request,
        "ai_suggestions.html",
        {
            "category": category,
            "page_title": f"AI Suggestions for {category.name}",
            "result_urls": result_urls,
        },
    )



class ClothingUploadView(View):
    def get(self, request, category_id=None):
        form = ClothingUploadForm()
        return render(request, 'upload.html', {'form': form})
    
    def post(self, request, category_id=None):
        form = ClothingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save()
            
            # Store upload ID in session for later use
            request.session['current_upload_id'] = upload.id
            
            return render(request, 'upload.html', {
                'form': ClothingUploadForm(),
                'upload': upload,
                'show_classify_button': True,
                'upload_id': upload.id 
            })
        
        return render(request, 'upload.html', {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class GetSuggestionsView(View):
    def post(self, request):
        data = json.loads(request.body)
        upload_id = data.get('upload_id')
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