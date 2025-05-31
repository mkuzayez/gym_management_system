from django.test import TestCase
from django.contrib.auth import get_user_model
from ..permissions import HasActiveSubscription
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta

class MockView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]
    
    def get(self, request):
        return None

class PermissionTests(TestCase):
    """
    Test cases for custom permissions
    """
    def setUp(self):
        User = get_user_model()
        
        # Create an admin user
        self.admin_user = User.objects.create_user(
            phone_number="9999999999",
            name="Admin User",
            password="adminpassword",
            is_staff=True
        )
        
        # Create a user with active subscription
        self.active_user = User.objects.create_user(
            phone_number="1234567890",
            name="Active User",
            password="testpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        # Create a user with expired subscription
        self.expired_user = User.objects.create_user(
            phone_number="0987654321",
            name="Expired User",
            password="testpassword",
            subscription_start=timezone.now().date() - timedelta(days=60),
            subscription_end=timezone.now().date() - timedelta(days=30)
        )
        
        self.factory = APIRequestFactory()
        self.view = MockView.as_view()
    
    def test_has_active_subscription_permission(self):
        """Test the HasActiveSubscription permission"""
        # Test with admin user
        request = self.factory.get('/fake-url/')
        request.user = self.admin_user
        
        permission = HasActiveSubscription()
        self.assertTrue(permission.has_permission(request, self.view))
        
        # Test with active subscription user
        request = self.factory.get('/fake-url/')
        request.user = self.active_user
        
        permission = HasActiveSubscription()
        self.assertTrue(permission.has_permission(request, self.view))
        
        # Test with expired subscription user
        request = self.factory.get('/fake-url/')
        request.user = self.expired_user
        
        permission = HasActiveSubscription()
        self.assertFalse(permission.has_permission(request, self.view))
