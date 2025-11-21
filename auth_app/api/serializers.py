"""Serializers for user authentication and user data representation.

This module contains serializers for:
  - UserSerializer: User model representation (id, email, fullname).
  - RegisterSerializer: User registration with password validation.
  - LoginSerializer: User login with email and password authentication.
"""

from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is responsible for converting User model instances to and from
    JSON representation. It includes the user's id, email, and fullname fields.

    Attributes:
        Meta: Configuration class for the serializer.
            model (User): The User model to serialize.
            fields (list): The fields to include in the serialized representation:
                - id: The unique identifier of the user.
                - email: The email address of the user.
                - fullname: The full name of the user.
            read_only_fields (list): Fields that are read-only and cannot be modified:
                - id: The user ID is automatically generated and immutable.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration.

    Handles new user registration by validating email, full name, and password.
    Ensures passwords match and creates a user with an associated authentication token.

    Attributes:
        password (CharField): Write-only password field with minimum length of 8.
        repeated_password (CharField): Write-only confirmation password field.
    """
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    repeated_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'fullname', 'password', 'repeated_password']
    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            password=validated_data['password']
        )

        Token.objects.create(user=user)
        
        return user
    
class LoginSerializer(serializers.Serializer):
    """Serializer for user login.

    Authenticates a user using email and password, returning the authenticated user
    or raising a validation error if credentials are invalid or the account is inactive.

    Attributes:
        email (EmailField): User email address.
        password (CharField): Write-only password field.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled."
            )
        
        # Add user to validated data
        data['user'] = user
        return data