from rest_framework import serializers
from .models import AuthUser
from django.core.validators import RegexValidator

class AuthUserSerializer(serializers.ModelSerializer):
    # password_validator = RegexValidator(
    #     regex='^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$',
    #     message="Password must contain at least one digit, one lowercase letter, one uppercase letter, and one special character."
    # )

    # Define the password field with the custom validator
    # password = serializers.CharField(
    #     write_only=True,
    #     required=True,
    #     validators=[password_validator],
    #     style={'input_type': 'password'}
    # )

    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'is_active', 'is_superuser', 'is_staff', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    # def create(self, validated_data):
    #     # Use the create_user method to handle password hashing
    #     user = AuthUser.objects.create_user(**validated_data)
    #     return user