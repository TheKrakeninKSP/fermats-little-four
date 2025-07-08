from django.shortcuts import render, get_object_or_404, redirect
from .models import Category
from .models import Product, Profile, WardrobeItem

from django.contrib.auth.decorators import login_required
from .forms import ProfileImageForm
import requests
from PIL import Image
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import messages

def home(request):
    categories = Category.objects.exclude(slug="uncategorized")
    context = {'categories': categories}
    return render(request, 'home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'category_detail.html', {
        'category': category,
        'products': products,
        'page_title': f"{category.name} - Products"
    })


def resize_image_to_512(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((512, 512))
    byte_io = BytesIO()
    img.save(byte_io, format='JPEG', quality=95)
    byte_io.seek(0)
    return byte_io


@login_required
def add_to_wardrobe(request,category_id):
    category = get_object_or_404(Category,id=category_id)
    WardrobeItem.objects.get_or_create(user=request.user,category=category)
    return redirect('home')

from .forms import ProfileImageForm
from .models import Profile

@login_required
def wardrobe(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
         # Store the old file
         old_image = None
         if profile.full_body_image:
             old_image = profile.full_body_image.path

         # Save the new one
         form.save()

         # Delete the old file if a new one was uploaded
         if 'full_body_image' in request.FILES and old_image:
             import os
             if os.path.exists(old_image):
                 os.remove(old_image)

         return redirect('wardrobe')

    else:
        form = ProfileImageForm(instance=profile)

    items = WardrobeItem.objects.filter(user=request.user).select_related('category')
    return render(request, 'wardrobe.html', {
        'wardrobe_items': items,
        'form': form
    })
@login_required
def remove_from_wardrobe(request, category_id):
    item = get_object_or_404(WardrobeItem, user=request.user, category_id=category_id)
    item.delete()
    return redirect('wardrobe')

@login_required
def try_on(request, category_id):
    
    profile = get_object_or_404(Profile, user=request.user)
    category = get_object_or_404(Category, id=category_id)
    if not profile.full_body_image:
        messages.error(request, "Please upload your full-body image first.")
        return redirect('wardrobe')

    # Full paths
    avatar_path = default_storage.path(profile.full_body_image.name)
    cloth_path = default_storage.path(category.image.name)

    # Resize and prepare images
    avatar_io = resize_image_to_512(avatar_path)
    cloth_io = resize_image_to_512(cloth_path)

    headers = {
        "x-rapidapi-key": "91de88b5a5msh84a5edba908ba7bp14306djsnddd6c65aa846",
        "x-rapidapi-host": "try-on-diffusion.p.rapidapi.com"
    }

    files = {
        "avatar_image": ("avatar.jpg", avatar_io, "image/jpeg"),
        "clothing_image": ("cloth.jpg", cloth_io, "image/jpeg")
    }

    response = requests.post(
        "https://try-on-diffusion.p.rapidapi.com/try-on-file",
        headers=headers,
        files=files,
        data={"seed": "-1"}
    )

    if response.status_code == 200:
        result_path = f"tryon_results/{request.user.username}_{category.id}.jpg"
        full_path = default_storage.save(result_path, BytesIO(response.content))
        result_url = settings.MEDIA_URL + result_path
    else:
        result_url = None

    items = WardrobeItem.objects.filter(user=request.user).select_related('category')
    form = ProfileImageForm(instance=profile)
    
    from time import time
    
    return render(request, 'wardrobe.html', {
        'wardrobe_items': items,
        'form': form,
        'result_url': result_url,
        'tried_on': category.name,
        'timestamp': int(time()),
    })