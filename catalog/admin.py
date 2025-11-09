from django.contrib import admin
from .models import (
    Category, Attribute, AttributeValue, Product, 
    ProductCategory, ProductVariant, VariantAttributeValue, ProductImage
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'status', 'created_at']
    list_filter = ['status', 'parent']
    search_fields = ['name']


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']
    list_filter = ['attribute']
    search_fields = ['value']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['url', 'alt', 'is_main', 'sort']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['code', 'price', 'status']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'brand', 'base_price', 'status', 'created_at']
    list_filter = ['status', 'brand']
    search_fields = ['sku', 'name']
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['code', 'product', 'price', 'status', 'created_at']
    list_filter = ['status', 'product']
    search_fields = ['code', 'product__name']


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['variant', 'attribute', 'attribute_value']
    list_filter = ['attribute']
    search_fields = ['variant__code']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main', 'sort', 'created_at']
    list_filter = ['is_main', 'product']

