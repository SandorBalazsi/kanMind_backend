"""Views for user authentication endpoints.

Provides API endpoints for user registration, login, logout, and user information retrieval.
All views handle authentication token generation and validation.
"""

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from auth_app.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Handle user registration.

    Accepts POST requests with email, fullname, password, and repeated_password.
    Creates a new user and returns an authentication token upon successful registration.

    Args:
        request: HTTP request containing user registration data.

    Returns:
        Response: 201 CREATED with token, fullname, email, and user_id on success.
        Response: 400 BAD REQUEST with validation errors on failure.
    """

    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()

        token = Token.objects.get(user=user)
        
        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    
    # Return errors if validation failed
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Handle user login.

    Accepts POST requests with email and password.
    Authenticates the user and returns an authentication token upon successful login.

    Args:
        request: HTTP request containing user login credentials.

    Returns:
        Response: 200 OK with token, fullname, email, and user_id on success.
        Response: 400 BAD REQUEST with validation errors on failure.
    """

    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)
        
        login(request, user)

        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
    
    # Return errors if validation failed
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Handle user logout.

    Logs out the authenticated user and deletes their authentication token.

    Args:
        request: HTTP request from an authenticated user.

    Returns:
        Response: 200 OK with logout success message.
    """

    logout(request)
    request.user.auth_token.delete()
    return Response({
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Retrieve current authenticated user information.

    Returns the profile data for the authenticated user making the request.

    Args:
        request: HTTP request from an authenticated user.

    Returns:
        Response: 200 OK with user data (id, email, fullname).
    """

    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_view(request):
    """Check if an email address exists in the system.

    Accepts GET requests with an 'email' query parameter.
    Returns user data if found, or a 404 error if not found.

    Args:
        request: HTTP request with 'email' query parameter.

    Returns:
        Response: 200 OK with user data (id, email, fullname) if email exists.
        Response: 400 BAD REQUEST if email parameter is missing.
        Response: 404 NOT FOUND if email does not exist.
    """
    email = request.query_params.get('email')
    
    if not email:
        return Response(
            {'error': 'Email parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)

        return Response({
            'id': user.id,
            'email': user.email,
            'fullname': user.fullname
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:

        return Response(
            {'error': 'Email not found'},
            status=status.HTTP_404_NOT_FOUND
        )