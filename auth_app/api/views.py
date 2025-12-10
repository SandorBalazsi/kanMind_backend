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
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    logout(request)
    request.user.auth_token.delete()
    return Response({
        'message': 'Logout successful'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_view(request):
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