from django.shortcuts import render, get_object_or_404
from .models import Category
from .models import Product

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
