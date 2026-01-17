"""
Authentication views for user registration and login.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user data."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        # Ensure user_id is in the token (for custom primary key)
        token['user_id'] = str(user.user_id)
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user data to response
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that returns user data along with tokens."""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    
    Expected payload:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890" (optional),
        "role": "guest" (optional, defaults to 'guest')
    }
    """
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create user with password
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=request.data.get('password'),
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            phone_number=serializer.validated_data.get('phone_number', ''),
            role=serializer.validated_data.get('role', 'guest')
        )
        
        # Return user data
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'User registered successfully',
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user's profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
