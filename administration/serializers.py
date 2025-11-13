from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
    """Serializer para Subrecursos del menú"""
    
    class Meta:
        model = Subresource
        fields = ['id', 'name', 'description', 'url', 'icon']


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer para Recursos del menú"""
    subresources = SubresourceSerializer(many=True, read_only=True, source='subs')
    
    class Meta:
        model = Resource
        fields = ['id', 'name', 'description', 'icon', 'subresources']


class RoleResourceSerializer(serializers.ModelSerializer):
    """Serializer para Permisos de Rol"""
    resource_name = serializers.CharField(source='resource.name', read_only=True)
    subresource_name = serializers.CharField(source='subresource.name', read_only=True)
    
    class Meta:
        model = RoleResource
        fields = ['id', 'role', 'resource', 'resource_name', 'subresource', 'subresource_name']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para Roles"""
    permissions = RoleResourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para JWT que acepta email o username.
    Compatible con el comportamiento del login de clientes.
    """
    username_field = 'username'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo username acepte email también
        self.fields[self.username_field] = serializers.CharField(
            help_text='Username o email del usuario'
        )
    
    def validate(self, attrs):
        username_or_email = attrs.get('username')
        password = attrs.get('password')
        
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
            raise serializers.ValidationError('Credenciales inválidas')
        
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo')
        
        # Establecer el usuario para que TokenObtainPairSerializer genere los tokens
        attrs['username'] = user.username
        
        # Llamar al validate del padre para generar los tokens
        data = super().validate(attrs)
        
        return data
