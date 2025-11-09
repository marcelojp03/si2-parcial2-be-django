from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleFactViewSet, ForecastModelViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'sales', SaleFactViewSet, basename='sale-fact')
router.register(r'forecasts', ForecastModelViewSet, basename='forecast')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
