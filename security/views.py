from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import User, Role, Resource, Subresource, RoleResource
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    RoleSerializer,
    ResourceSerializer,
    SubresourceSerializer,
    RoleResourceSerializer,
    MenuSerializer
)


@extend_schema(
    summary="Login de usuario",
    description="Autentica un usuario y crea una sesión",
    request=LoginSerializer,
    responses={200: UserSerializer},
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login de usuario"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Login exitoso',
            'user': user_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout de usuario",
    description="Cierra la sesión del usuario actual",
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout de usuario"""
    logout(request)
    return Response({'message': 'Logout exitoso'})


@extend_schema(
    summary="Usuario actual",
    description="Obtiene la información del usuario autenticado",
    responses={200: UserSerializer},
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Obtiene el usuario actual"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Menú del usuario",
    description="Obtiene el menú dinámico basado en permisos del usuario",
    responses={200: MenuSerializer(many=True)},
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_menu_view(request):
    """Obtiene el menú del usuario según sus permisos"""
    user = request.user
    
    # Obtener el rol del usuario a través de los grupos
    user_group = user.groups.first()
    if not user_group or not hasattr(user_group, 'role'):
        return Response([])
    
    user_role = user_group.role
    
    # Obtener recursos permitidos para el rol
    role_resources = RoleResource.objects.filter(
        role=user_role,
        can_view=True
    ).select_related('resource').prefetch_related('resource__subresources')
    
    menu = []
    for role_resource in role_resources:
        resource = role_resource.resource
        
        # Obtener subrecursos permitidos
        subresources = []
        for subresource in resource.subresources.all():
            # Verificar permisos específicos del subrecurso
            sub_permission = RoleResource.objects.filter(
                role=user_role,
                resource=resource,
                subresource=subresource,
                can_view=True
            ).exists()
            
            if sub_permission:
                subresources.append({
                    'id': subresource.id,
                    'name': subresource.name,
                    'endpoint': subresource.endpoint,
                    'method': subresource.method
                })
        
        menu.append({
            'id': resource.id,
            'name': resource.name,
            'icon': resource.icon,
            'route': resource.route,
            'subresources': subresources
        })
    
    return Response(menu)


@extend_schema_view(
    list=extend_schema(summary="Listar usuarios", tags=['Auth']),
    retrieve=extend_schema(summary="Obtener usuario", tags=['Auth']),
    create=extend_schema(summary="Crear usuario", tags=['Auth']),
    update=extend_schema(summary="Actualizar usuario", tags=['Auth'])
)
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios"""
    queryset = User.objects.prefetch_related('groups__role').all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @extend_schema(
        summary="Cambiar contraseña",
        request={'new_password': 'string'},
        tags=['Auth']
    )
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Cambia la contraseña de un usuario"""
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Contraseña actualizada'})


@extend_schema_view(
    list=extend_schema(summary="Listar roles", tags=['Auth']),
    retrieve=extend_schema(summary="Obtener rol", tags=['Auth']),
    create=extend_schema(summary="Crear rol", tags=['Auth']),
    update=extend_schema(summary="Actualizar rol", tags=['Auth'])
)
class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar roles"""
    queryset = Role.objects.prefetch_related('role_resources').all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(summary="Listar recursos", tags=['Auth']),
    retrieve=extend_schema(summary="Obtener recurso", tags=['Auth']),
    create=extend_schema(summary="Crear recurso", tags=['Auth']),
    update=extend_schema(summary="Actualizar recurso", tags=['Auth'])
)
class ResourceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar recursos"""
    queryset = Resource.objects.prefetch_related('subresources').all()
    serializer_class = ResourceSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(summary="Listar permisos", tags=['Auth']),
    retrieve=extend_schema(summary="Obtener permiso", tags=['Auth']),
    create=extend_schema(summary="Asignar permiso", tags=['Auth']),
    update=extend_schema(summary="Actualizar permiso", tags=['Auth'])
)
class RoleResourceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar permisos de roles"""
    queryset = RoleResource.objects.select_related('role', 'resource', 'subresource').all()
    serializer_class = RoleResourceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        return queryset
