from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema, extend_schema_view
from ecommerce.responses import ApiResponse
from .models import User, Role, Resource, Subresource, RoleResource
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    RoleSerializer,
    ResourceSerializer,
    SubresourceSerializer,
    RoleResourceSerializer,
    CustomTokenObtainPairSerializer,
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
    summary="Login de administrador (API)",
    description="Autentica un administrador por API. Retorna user_type='admin' para que el frontend redirija al panel de administración. Solo usuarios staff pueden usar este endpoint.",
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login_view(request):
    """
    Login para administradores.
    Acepta username o email.
    Solo permite usuarios con is_staff=True.
    """
    from .serializers import AdminLoginSerializer
    from django.contrib.auth import authenticate, get_user_model
    
    serializer = AdminLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username_or_email = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    User = get_user_model()
    
    # Intentar autenticar con username
    user = authenticate(username=username_or_email, password=password)
    
    # Si falla, intentar buscar por email
    if user is None:
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Verificar que sea staff o superuser
    if not user.is_staff and not user.is_superuser:
        return Response(
            {'error': 'Access denied. Admin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Login con sesión de Django (para acceso al /admin/)
    login(request, user)
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        },
        'user_type': 'admin',  # Identificador para el frontend
        'message': 'Admin login successful'
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Registro de nuevo usuario",
    description="Crea un nuevo usuario en el sistema",
    request=UserCreateSerializer,
    responses={201: UserSerializer},
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registro de nuevo usuario"""
    serializer = UserCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)
        return ApiResponse.success(
            data=user_serializer.data,
            message="Usuario registrado exitosamente",
            http_code=201
        )
    
    return ApiResponse.validation_error(serializer.errors)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista JWT personalizada que acepta email o username.
    Compatible con el login de clientes.
    """
    serializer_class = CustomTokenObtainPairSerializer


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
    responses={200: ResourceSerializer(many=True)},
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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        return queryset


@extend_schema(
    summary="Obtener menú dinámico",
    description="Construye el menú del admin basado en los roles y permisos del usuario autenticado",
    responses={200: ResourceSerializer(many=True)},
    tags=['Menu']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_menu(request):
    """
    Endpoint que construye el menú dinámico para el usuario.
    Retorna los recursos y subrecursos permitidos según sus roles.
    """
    try:
        user = request.user
        
        # Obtener grupos (roles) del usuario
        user_groups = user.groups.all()
        
        if not user_groups:
            return Response({
                'success': True,
                'message': 'Usuario sin roles asignados',
                'data': []
            })
        
        # Obtener roles asociados a los grupos
        role_ids = []
        for group in user_groups:
            if hasattr(group, 'role'):
                role_ids.append(group.role.id)
        
        if not role_ids:
            return Response({
                'success': True,
                'message': 'Sin recursos asignados',
                'data': []
            })
        
        # Obtener permisos (RoleResource) de esos roles
        role_resources = RoleResource.objects.filter(
            role_id__in=role_ids
        ).select_related('resource', 'subresource')
        
        # Agrupar por recurso
        resources_dict = {}
        
        for rr in role_resources:
            resource_id = rr.resource.id
            
            if resource_id not in resources_dict:
                resources_dict[resource_id] = {
                    'id': rr.resource.id,
                    'name': rr.resource.name,
                    'description': rr.resource.description,
                    'icon': rr.resource.icon,
                    'order': rr.resource.order,
                    'subresources': []
                }
            
            # Agregar subrecurso si no está duplicado
            subresource_data = {
                'id': rr.subresource.id,
                'name': rr.subresource.name,
                'description': rr.subresource.description,
                'url': rr.subresource.url,
                'icon': rr.subresource.icon
            }
            
            # Evitar duplicados
            if subresource_data not in resources_dict[resource_id]['subresources']:
                resources_dict[resource_id]['subresources'].append(subresource_data)
        
        # Convertir a lista y ordenar
        menu_list = list(resources_dict.values())
        menu_list.sort(key=lambda x: (x['order'], x['name']))
        
        # Ordenar subrecursos dentro de cada recurso
        for resource in menu_list:
            resource['subresources'].sort(key=lambda x: x['name'])
        
        return Response({
            'success': True,
            'message': 'Menú construido',
            'data': menu_list
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al construir menú: {str(e)}',
            'data': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
