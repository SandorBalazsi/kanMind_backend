from rest_framework import serializers
from ..models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    repeated_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'fullname', 'password', 'repeated_password']
    
    def validate(self, data):
        """Ensure the provided passwords match.

        Raises a `ValidationError` keyed on `repeated_password` when the two
        password fields differ.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        """Create a new `User` and associated auth `Token`.

        Uses the email as username to remain compatible with Django's
        `create_user` manager. Removes the `repeated_password` key before
        creating the user.
        """
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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """Authenticate credentials and return the user in validated data.

        Raises `ValidationError` for invalid credentials or inactive accounts.
        On success the authenticated `user` object is added to the returned
        validated data under the `user` key.
        """
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

        data['user'] = user
        return data