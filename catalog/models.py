from django.db import models


class Category(models.Model):
    """
    Categoría de productos con soporte para jerarquía (árbol).
    Ejemplo: Electrónica > Laptops, Ropa > Hombre > Camisetas
    """
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        "self", 
        null=True, 
        blank=True, 
        related_name="children", 
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=16, 
        default="ACTIVE",
        choices=[("ACTIVE", "Activo"), ("INACTIVE", "Inactivo")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'catalog_category'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Attribute(models.Model):
    """
    Atributo para variantes de productos.
    Ejemplo: Talla, Color, Material, Capacidad
    """
    name = models.CharField(max_length=80, unique=True)
    
    class Meta:
        db_table = 'catalog_attribute'
        verbose_name = 'Atributo'
        verbose_name_plural = 'Atributos'

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """
    Valor específico de un atributo.
    Ejemplo: Talla -> S, M, L, XL | Color -> Rojo, Azul, Negro
    """
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=80)
    
    class Meta:
        db_table = 'catalog_attribute_value'
        verbose_name = 'Valor de Atributo'
        verbose_name_plural = 'Valores de Atributos'
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    """
    Producto base (maestro).
    Puede tener múltiples variantes.
    """
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    brand = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=16,
        default="ACTIVE",
        choices=[("ACTIVE", "Activo"), ("INACTIVE", "Inactivo"), ("DRAFT", "Borrador")]
    )
    categories = models.ManyToManyField(Category, through="ProductCategory", related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'catalog_product'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class ProductCategory(models.Model):
    """
    Relación M2M entre Product y Category.
    Permite asignar múltiples categorías a un producto.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'catalog_product_category'
        unique_together = ('product', 'category')


class ProductVariant(models.Model):
    """
    Variante de un producto (SKU específico).
    Ejemplo: Camiseta Roja Talla M, Laptop 16GB RAM
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    code = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=16,
        default="ACTIVE",
        choices=[("ACTIVE", "Activo"), ("INACTIVE", "Inactivo")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'catalog_product_variant'
        verbose_name = 'Variante de Producto'
        verbose_name_plural = 'Variantes de Productos'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['product', 'status']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.code}"


class VariantAttributeValue(models.Model):
    """
    Asignación de atributos a una variante.
    Ejemplo: Variante X -> Talla: M, Color: Rojo
    """
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="attr_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'catalog_variant_attribute_value'
        unique_together = ("variant", "attribute")
        verbose_name = 'Atributo de Variante'
        verbose_name_plural = 'Atributos de Variantes'

    def __str__(self):
        return f"{self.variant.code} -> {self.attribute_value}"


class ProductImage(models.Model):
    """
    Imágenes de productos.
    Soporta múltiples imágenes ordenadas.
    Compatible con S3 y URLs locales.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    
    # S3 Storage (preferido para producción)
    s3_bucket = models.CharField(max_length=100, blank=True, null=True, help_text="Bucket S3 donde está almacenada la imagen")
    s3_key = models.CharField(max_length=500, blank=True, null=True, help_text="Key (path) de la imagen en S3")
    
    # URL Fallback (para desarrollo o URLs externas)
    url = models.CharField(max_length=400, blank=True, null=True, help_text="URL directa de la imagen (fallback si no usa S3)")
    
    # Metadata
    alt = models.CharField(max_length=150, blank=True)
    is_main = models.BooleanField(default=False)
    sort = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'catalog_product_image'
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        indexes = [
            models.Index(fields=["product", "sort"]),
        ]
        ordering = ['sort']

    def __str__(self):
        return f"{self.product.name} - Imagen {self.sort}"
    
    def get_image_url(self, expiration=3600):
        """
        Obtiene la URL de la imagen.
        - Si tiene s3_bucket y s3_key: genera presigned URL
        - Sino: retorna url directa
        """
        if self.s3_bucket and self.s3_key:
            from apps.core.services.aws_s3 import generate_presigned_url
            return generate_presigned_url(self.s3_bucket, self.s3_key, expiration)
        return self.url

