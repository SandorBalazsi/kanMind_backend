from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from auth_app.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):

    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create the user
        user = serializer.save()
        
        # Automatically login the user
        login(request, user)
        
        # Return user data
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    # Return errors if validation failed
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        login(request, user)

        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
    
    # Return errors if validation failed
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    logout(request)
    return Response({
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):

    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_view(request):
    """
    Check if email exists (for your frontend)
    POST /api/auth/check-email/
    Body: {"email": "..."}
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )