from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    login_view,
    logout_view,
    admin_login_view,
    current_user_view,
    user_menu_view,
    get_menu,
    UserViewSet,
    RoleViewSet,
    ResourceViewSet,
    RoleResourceViewSet,
    register_view,
    CustomTokenObtainPairView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'permissions', RoleResourceViewSet, basename='permission')

urlpatterns = [
    # JWT endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Auth endpoints (legacy/session)
    path('login/', login_view, name='login'),
    path('admin-login/', admin_login_view, name='admin-login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('me/', current_user_view, name='current-user'),
    path('menu/', get_menu, name='menu'),  # Menú dinámico
    path('menu/legacy/', user_menu_view, name='user-menu'),  # Legacy
    
    # CRUD endpoints
    path('', include(router.urls)),
]
