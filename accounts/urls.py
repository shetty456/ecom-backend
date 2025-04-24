from django.urls import path
from .views import (
    RequestOTPView,
    VerifyOTPView,
    UserProfileView,
    UserUpdateView
)

app_name = 'accounts'

urlpatterns = [
    path('otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),
] 
