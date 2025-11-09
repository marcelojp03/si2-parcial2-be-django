from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    login_view,
    logout_view,
    current_user_view,
    user_menu_view,
    UserViewSet,
    RoleViewSet,
    ResourceViewSet,
    RoleResourceViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'permissions', RoleResourceViewSet, basename='permission')

urlpatterns = [
    # Auth endpoints
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', current_user_view, name='current-user'),
    path('menu/', user_menu_view, name='user-menu'),
    
    # CRUD endpoints
    path('', include(router.urls)),
]
