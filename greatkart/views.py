from django.shortcuts import render
from store.models import Product, ReviewRating, Testimonial


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get all reviews for available products
    reviews = ReviewRating.objects.filter(
        product__in=products,
        status=True,
    )

    # Get all testimonials
    testimonials = Testimonial.objects.all()

    context = {
        'products': products,
        'reviews': reviews,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)


def create_admin(request):
    """
    Create a superuser account. This endpoint should be removed or
    protected in production.
    """
    from django.contrib.auth import get_user_model
    from django.http import HttpResponse

    # Only allow in DEBUG mode
    from django.conf import settings
    if not settings.DEBUG:
        return HttpResponse("Forbidden", status=403)

    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            email="rohith.allaka@gmail.com",
            username="RohithKumar",
            password="rohith@2006",
            first_name='RohithKumar',
            last_name='Allaka',
        )
        return HttpResponse("Superuser created")
    return HttpResponse("Superuser already exists")