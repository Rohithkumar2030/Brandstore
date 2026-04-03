from django.contrib import admin
from .models import Product, ReviewRating, ProductGallery, ProductVariation, Testimonial
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0
    fields = ('color', 'size', 'stock', 'is_active')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline, ProductVariationInline]

class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'stock', 'is_active')
    list_filter = ('product', 'color', 'size', 'is_active')
    list_editable = ('stock', 'is_active')

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'created_at')

admin.site.register(Product, ProductAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
