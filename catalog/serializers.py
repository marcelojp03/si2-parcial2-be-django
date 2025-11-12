from rest_framework import serializers
from .models import Category, Attribute, AttributeValue, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para Categorías"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children', 'status', 'created_at']
        read_only_fields = ['created_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer para Valores de Atributos"""
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer para Atributos"""
    values = AttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'values']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer para Variantes de Producto"""
    attributes = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'code', 'product', 'price', 'attributes', 'status',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_attributes(self, obj):
        """Obtiene los atributos de la variante"""
        variant_attrs = obj.attr_values.select_related('attribute', 'attribute_value').all()
        return [
            {
                'attribute': attr.attribute.name,
                'value': attr.attribute_value.value
            }
            for attr in variant_attrs
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para lista de productos"""
    category_names = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'brand',
            'category_names', 'main_image', 'price_range',
            'status', 'created_at'
        ]
    
    def get_category_names(self, obj):
        return [cat.name for cat in obj.categories.all()]
    
    def get_main_image(self, obj):
        first_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if first_image:
            return first_image.get_image_url()
        return None
    
    def get_price_range(self, obj):
        variants = obj.variants.filter(status='ACTIVE')
        if variants.exists():
            prices = variants.values_list('price', flat=True)
            min_price = min(prices)
            max_price = max(prices)
            if min_price == max_price:
                return {'price': float(min_price)}
            return {'min': float(min_price), 'max': float(max_price)}
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para producto individual"""
    categories = CategorySerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'brand',
            'base_price', 'categories', 'variants', 'images',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_images(self, obj):
        return [
            {
                'id': img.id,
                'url': img.get_image_url(),
                'alt': img.alt,
                'is_main': img.is_main,
                'sort': img.sort
            }
            for img in obj.images.all().order_by('sort')
        ]
