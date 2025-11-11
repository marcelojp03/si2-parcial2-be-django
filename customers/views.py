"""
Views para autenticación de clientes (Customer Authentication)
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from customers.models import Customer

User = get_user_model()
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    CustomerSerializer,
    ChangePasswordSerializer,
    ProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Registro de nuevos clientes.
    Crea un User y un Customer asociado.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def get_queryset(self):
        return User.objects.all()

    @extend_schema(
        tags=['Auth'],
        summary='Register new customer',
        description='Create a new customer account with user credentials',
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description='Customer registered successfully',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'email': 'john@example.com',
                                'first_name': 'John',
                                'last_name': 'Doe'
                            },
                            'message': 'User registered successfully'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation errors')
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Login de clientes.
    Autentica y devuelve tokens JWT (access + refresh).
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['Auth'],
        summary='Customer login',
        description='Authenticate customer and get JWT tokens',
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Login successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'email': 'john@example.com',
                                'first_name': 'John',
                                'last_name': 'Doe'
                            },
                            'tokens': {
                                'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                            },
                            'message': 'Login successful'
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description='Invalid credentials')
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Intentar autenticar con username o email
        user = authenticate(username=username, password=password)
        
        # Si falla, intentar buscar por email y autenticar
        if user is None:
            try:
                user_by_email = User.objects.get(email=username)
                user = authenticate(username=user_by_email.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar que sea un cliente (tiene Customer asociado)
        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'customer': {
                'id': customer.id,
                'phone': customer.phone,
                'address': customer.address,
                'city': customer.city,
                'country': customer.country,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user_type': 'customer',  # Identificador para el frontend
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logout de clientes.
    Invalida el refresh token.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Customer logout',
        description='Logout customer by blacklisting refresh token',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
                },
                'required': ['refresh']
            }
        },
        responses={
            200: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid token')
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Ver y editar perfil del cliente autenticado.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    @extend_schema(
        tags=['Auth'],
        summary='Get customer profile',
        description='Get authenticated customer profile information',
        responses={
            200: ProfileSerializer,
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Auth'],
        summary='Update customer profile',
        description='Update authenticated customer profile information',
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description='Validation errors'),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=['Auth'],
        summary='Partial update customer profile',
        description='Partially update authenticated customer profile information',
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description='Validation errors'),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        """Obtener el Customer del usuario autenticado"""
        return Customer.objects.get(user=self.request.user)


class ChangePasswordView(APIView):
    """
    Cambiar contraseña del cliente autenticado.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Change password',
        description='Change password for authenticated customer',
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='Password changed successfully',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={'message': 'Password changed successfully'}
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation errors or incorrect old password'),
            401: OpenApiResponse(description='Authentication required')
        }
    )
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Verificar contraseña actual
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
