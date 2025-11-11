from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role, Resource, Subresource, RoleResource


class UserSerializer(serializers.ModelSerializer):
    """Serializer para Usuarios"""
    role_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'avatar', 'is_active',
            'date_joined', 'last_login', 'role_name'
        ]
        read_only_fields = ['date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}
    
    def get_role_name(self, obj):
        """Obtiene el nombre del rol del usuario a través de los grupos"""
        try:
            group = obj.groups.first()
            if group and hasattr(group, 'role'):
                return group.role.name
            return None
        except:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas')
            if not user.is_active:
                raise serializers.ValidationError('Usuario inactivo')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Debe incluir username y password')
        
        return attrs


class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer para login de administradores por API.
    Acepta username o email.
    """
    username = serializers.CharField(
        required=True,
        help_text='Username o email del administrador'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class SubresourceSerializer(serializers.ModelSerializer):
    """Serializer para Subrecursos"""
    
    class Meta:
        model = Subresource
        fields = ['id', 'resource', 'name', 'endpoint', 'method']


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer para Recursos"""
    subresources = SubresourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'name', 'icon', 'route', 'subresources']


class RoleResourceSerializer(serializers.ModelSerializer):
    """Serializer para Permisos de Rol"""
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    subresource_name = serializers.CharField(source='subresource.name', read_only=True)
    
    class Meta:
        model = RoleResource
        fields = [
            'id', 'role', 'resource', 'resource_name',
            'subresource', 'subresource_name', 'can_view',
            'can_create', 'can_update', 'can_delete'
        ]


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para Roles"""
    permissions = RoleResourceSerializer(many=True, read_only=True, source='role_resources')
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']


class MenuSerializer(serializers.Serializer):
    """Serializer para el menú dinámico del usuario"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    icon = serializers.CharField()
    route = serializers.CharField()
    subresources = serializers.ListField()
