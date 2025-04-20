from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import OTP
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.phone = '9876543210'
        self.name = 'Test User'
        self.request_otp_url = reverse('accounts:request-otp')
        self.verify_otp_url = reverse('accounts:verify-otp')
        self.profile_url = reverse('accounts:user-profile')
        self.update_profile_url = reverse('accounts:profile-update')
        
        # Test user data
        self.user_data = {
            'phone': '1234567890',
            'name': 'Test User',
            'password': 'testpass123'
        }
    
    def test_otp_request_new_user(self):
        """Test OTP request for new user"""
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('otp', response.data)
        
        # Verify user was created
        user = User.objects.get(phone=self.phone)
        self.assertFalse(user.is_verified)
    
    def test_otp_request_existing_user(self):
        """Test OTP request for existing user"""
        # Create existing user
        user = User.objects.create_user(phone=self.phone)
        
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('otp', response.data)
        
        # Verify new OTP was created
        otp = OTP.objects.filter(user=user).latest('created_at')
        self.assertEqual(otp.user, user)
    
    def test_otp_verification_new_user(self):
        """Test OTP verification for new user"""
        # Request OTP
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        otp = response.data['otp']
        
        # Verify OTP
        response = self.client.post(self.verify_otp_url, {
            'phone': self.phone,
            'otp': otp
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['user']['is_verified'])
        self.assertIn('tokens', response.data)
    
    def test_otp_verification_existing_user(self):
        """Test OTP verification for existing user"""
        # Create user with complete profile
        user = User.objects.create_user(
            phone=self.phone,
            name=self.name
        )
        
        # Request OTP
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        otp = response.data['otp']
        
        # Verify OTP
        response = self.client.post(self.verify_otp_url, {
            'phone': self.phone,
            'otp': otp
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['user']['is_verified'])
        self.assertIn('tokens', response.data)
    
    def test_profile_update(self):
        """Test profile update after OTP verification"""
        # Create user and verify OTP
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        otp = response.data['otp']
        
        response = self.client.post(self.verify_otp_url, {
            'phone': self.phone,
            'otp': otp
        })
        tokens = response.data['tokens']
        
        # Update profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.put(self.update_profile_url, {
            'name': self.name
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['name'], self.name)
    
    def test_invalid_otp(self):
        """Test verification with invalid OTP"""
        # Request OTP
        self.client.post(self.request_otp_url, {'phone': self.phone})
        
        # Try verification with wrong OTP
        response = self.client.post(self.verify_otp_url, {
            'phone': self.phone,
            'otp': '000000'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid OTP', str(response.data))
    
    def test_expired_otp(self):
        """Test verification with expired OTP"""
        # Request OTP
        response = self.client.post(self.request_otp_url, {'phone': self.phone})
        otp = response.data['otp']
        
        # Simulate OTP expiry
        otp_obj = OTP.objects.latest('created_at')
        otp_obj.expires_at = timezone.now() - timedelta(minutes=1)
        otp_obj.save()
        
        # Try verification
        response = self.client.post(self.verify_otp_url, {
            'phone': self.phone,
            'otp': otp
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('OTP has expired', str(response.data))
    
    def test_get_profile_unauthorized(self):
        """Test profile access without authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 