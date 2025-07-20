from django.shortcuts import render
from store.models import Product, ReviewRating
from django.contrib.auth import get_user_model
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
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(email="rohith.allaka@gmail.com",username="RohithKumar",password="rohith@2006",first_name='RohithKumar',last_name='Allaka')
        return HttpResponse("Superuser created")
    return HttpResponse("Superuser already exists")