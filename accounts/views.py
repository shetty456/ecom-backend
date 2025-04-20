from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import OTP
from .serializers import (
    PhoneSerializer,
    OTPVerificationSerializer,
    UserSerializer,
    UserUpdateSerializer
)

User = get_user_model()

class RequestOTPView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        
        # Get or create user with phone
        user, _ = User.objects.get_or_create(phone=phone)
        
        # Generate OTP
        otp = OTP.objects.create(user=user)
        
        # In production, send OTP via SMS
        # For development, return OTP in response
        return Response({
            'message': 'OTP sent successfully',
            'otp': otp.otp  # Remove in production
        })


class VerifyOTPView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'OTP verified successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        })


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(instance).data
        })
