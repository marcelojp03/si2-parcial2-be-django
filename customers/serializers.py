"""
Serializers para autenticación de clientes (Customer Authentication)
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from customers.models import Customer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para datos del usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_staff', 'is_superuser']


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer para datos del cliente"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone', 'address', 'city', 'country', 'postal_code', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos clientes"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")
    
    # Campos opcionales del cliente
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name',
                  'phone', 'address', 'city', 'country', 'postal_code']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validar email único
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        
        return attrs
    
    def validate_username(self, value):
        """Validar que el username no pertenezca a un usuario staff/admin"""
        if User.objects.filter(username=value, is_staff=True).exists():
            raise serializers.ValidationError("This username is reserved.")
        return value
    
    def validate_email(self, value):
        """Validar que el email no pertenezca a un usuario staff/admin"""
        if User.objects.filter(email=value, is_staff=True).exists():
            raise serializers.ValidationError("This email is reserved.")
        return value

    def create(self, validated_data):
        """Crear usuario y cliente"""
        # Extraer campos del cliente
        phone = validated_data.pop('phone', '')
        address = validated_data.pop('address', '')
        city = validated_data.pop('city', '')
        country = validated_data.pop('country', '')
        postal_code = validated_data.pop('postal_code', '')
        validated_data.pop('password2')
        
        # Crear usuario (explícitamente como NO staff/superuser)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            is_staff=False,  # Los clientes NO son staff
            is_superuser=False  # Los clientes NO son superusers
        )
        
        # Crear cliente asociado
        Customer.objects.create(
            user=user,
            phone=phone,
            address=address,
            city=city,
            country=country,
            postal_code=postal_code
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login de clientes - acepta username o email"""
    username = serializers.CharField(
        required=True,
        help_text="Username o Email del usuario"
    )
    password = serializers.CharField(
        required=True, 
        write_only=True, 
        style={'input_type': 'password'}
    )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True, label="Confirm New Password")

    def validate(self, attrs):
        """Validar que las contraseñas nuevas coincidan"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer para ver y editar perfil completo del cliente"""
    user = UserSerializer(read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'email', 'first_name', 'last_name', 
                  'phone', 'address', 'city', 'country', 'postal_code', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def update(self, instance, validated_data):
        """Actualizar usuario y cliente"""
        user_data = validated_data.pop('user', {})
        
        # Actualizar datos del User
        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        
        # Actualizar datos del Customer
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.save()
        
        return instance
