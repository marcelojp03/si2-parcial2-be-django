from catalog.models import Product, ProductImage, Category

print(f'✅ Products in DB: {Product.objects.count()}')
print(f'✅ Images in DB: {ProductImage.objects.count()}')
print(f'✅ Categories in DB: {Category.objects.count()}')

print('\n📦 Products per category:')
cats = Category.objects.filter(
    name__in=["Men's T-Shirts", "Ladies' T-Shirts", "Men's Outerwear", "Ladies' Outerwear"]
)
for c in cats:
    count = Product.objects.filter(categories=c).count()
    print(f'  - {c.name}: {count}')
