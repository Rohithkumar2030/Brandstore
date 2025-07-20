from django.shortcuts import render
from store.models import Product, ReviewRating
from django.contrib.auth.models import User
from django.http import HttpResponse

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        return HttpResponse("Superuser created")
    return HttpResponse("Superuser already exists")