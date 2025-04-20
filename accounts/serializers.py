from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    
    def validate_phone(self, value):
        # Add your phone validation logic here
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return value

class OTPVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        otp_input = attrs.get('otp')
        
        try:
            user = User.objects.get(phone=phone)
            otp_obj = user.otps.filter(is_verified=False).latest('created_at')
            
            if not otp_obj.is_valid():
                raise serializers.ValidationError("OTP has expired")
            
            if not otp_obj.verify(otp_input):
                raise serializers.ValidationError("Invalid OTP")
            
            attrs['user'] = user
            return attrs
            
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this phone number")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("No active OTP found")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'name', 'role', 'is_verified', 'created_at']
        read_only_fields = ['is_verified', 'created_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name'] 