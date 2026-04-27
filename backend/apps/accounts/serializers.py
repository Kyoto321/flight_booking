from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, OTPToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'is_phone_verified', 'is_corporate', 'home_airport')
        read_only_fields = ('id', 'is_phone_verified')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'middle_name', 'gender', 'dob', 'avatar')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'phone', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone=validated_data.get('phone') or None,
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTPToken.PURPOSE_CHOICES)

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=OTPToken.PURPOSE_CHOICES)
