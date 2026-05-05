import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from .models import OTPToken, Profile
from .serializers import (
    RegisterSerializer, UserSerializer, OTPSerializer, 
    ResendOTPSerializer, ProfileSerializer
)

User = get_user_model()

def generate_otp(user, purpose):
    code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = timezone.now() + timedelta(minutes=10)
    OTPToken.objects.create(
        user=user,
        code=code,
        purpose=purpose,
        expires_at=expires_at
    )

    subject = f"Your {purpose} OTP code"
    message = (
        f"Hello {user.email},\n\n"
        f"Your verification code is: {code}\n"
        "This code expires in 10 minutes.\n\n"
        "If you did not request this, please ignore this message.\n"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=True)
    print(f"OTP for {user.email} ({purpose}): {code}")
    return code

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            generate_otp(user, 'REGISTER')
            return Response({
                "message": "User registered successfully. Please verify your email/phone with the OTP sent.",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            purpose = serializer.validated_data['purpose']
            
            try:
                user = User.objects.get(email=email)
                otp = OTPToken.objects.filter(
                    user=user, 
                    code=code, 
                    purpose=purpose, 
                    used=False,
                    expires_at__gt=timezone.now()
                ).latest('created_at')
                
                otp.used = True
                otp.save()
                
                if purpose == 'REGISTER':
                    user.is_active = True
                    user.is_phone_verified = True
                    user.save()
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "OTP verified successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
                
            except (User.DoesNotExist, OTPToken.DoesNotExist):
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']
            try:
                user = User.objects.get(email=email)
                generate_otp(user, purpose)
                return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            generate_otp(user, 'RESET')
            return Response(
                {"message": "Password reset OTP sent to your email."},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not all([email, code, new_password]):
            return Response(
                {"error": "Email, code, and new password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            otp = OTPToken.objects.filter(
                user=user,
                code=code,
                purpose='RESET',
                used=False,
                expires_at__gt=timezone.now()
            ).latest('created_at')
            
            otp.used = True
            otp.save()
            
            user.set_password(new_password)
            user.save()
            
            return Response(
                {"message": "Password reset successfully. You can now login with your new password."},
                status=status.HTTP_200_OK
            )
        except (User.DoesNotExist, OTPToken.DoesNotExist):
            return Response({"error": "Invalid or expired reset code"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {"error": "User account is not active. Please verify OTP first."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
