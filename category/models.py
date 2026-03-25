from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    # Tax fields - default 9% each, except Apparel which has 2.5%
    cgst          = models.DecimalField(max_digits=4, decimal_places=2, default=9.00)
    sgst          = models.DecimalField(max_digits=4, decimal_places=2, default=9.00)

    def save(self, *args, **kwargs):
        # Ensure Apparel category always has 2.5% tax rates
        if self.category_name.lower() == 'Apparel':
            self.cgst = 2.50
            self.sgst = 2.50
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
            return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
