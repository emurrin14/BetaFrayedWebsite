from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product, ProductImage, Color, Product_Variant, Size
from django.utils.html import format_html

# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return ""
    image_preview.short_description = "Preview"

class ProductVariantInline(admin.TabularInline):
    model = Product_Variant
    extra = 1
    autocomplete_fields = ['color', 'size'] 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock', 'isinstock', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name', 'sku', 'description')
    list_filter = ('isinstock', 'tags')
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order',)
    search_fields = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)

@admin.register(Product_Variant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'stock')
    list_filter = ('color', 'size', 'product') # Added filter by size
    search_fields = ('product__name', 'sku')
    autocomplete_fields = ['product', 'color', 'size']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'image')
    list_filter = ('product',)