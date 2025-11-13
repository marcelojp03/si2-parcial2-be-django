from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
