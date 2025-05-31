from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from ..models import Member
from rest_framework_simplejwt.tokens import RefreshToken

class SerializerTests(TestCase):
    """
    Test cases for serializers
    """
    def setUp(self):
        # Create a test member
        self.member = Member.objects.create_user(
            phone_number="1234567890",
            name="Test Member",
            password="testpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
    
    def test_member_serializer(self):
        """Test the MemberSerializer"""
        from ..serializers import MemberSerializer
        
        serializer = MemberSerializer(self.member)
        data = serializer.data
        
        self.assertEqual(data['name'], "Test Member")
        self.assertEqual(data['phone_number'], "1234567890")
        self.assertTrue(data['has_active_subscription'])
        
    def test_login_serializer(self):
        """Test the LoginSerializer"""
        from ..serializers import LoginSerializer
        
        # Test valid login
        valid_data = {
            'phone_number': '1234567890',
            'password': 'testpassword'
        }
        serializer = LoginSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Test invalid phone number
        invalid_phone = {
            'phone_number': '9999999999',
            'password': 'testpassword'
        }
        serializer = LoginSerializer(data=invalid_phone)
        self.assertFalse(serializer.is_valid())
        self.assertIn('error', serializer.errors)
        
        # Test invalid password
        invalid_password = {
            'phone_number': '1234567890',
            'password': 'wrongpassword'
        }
        serializer = LoginSerializer(data=invalid_password)
        self.assertFalse(serializer.is_valid())
        self.assertIn('error', serializer.errors)


class AuthViewTests(APITestCase):
    """
    Test cases for authentication views
    """
    def setUp(self):
        # Create a test member
        self.member = Member.objects.create_user(
            phone_number="1234567890",
            name="Test Member",
            password="testpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        # Create an expired member
        self.expired_member = Member.objects.create_user(
            phone_number="0987654321",
            name="Expired Member",
            password="testpassword",
            subscription_start=timezone.now().date() - timedelta(days=60),
            subscription_end=timezone.now().date() - timedelta(days=30)
        )
    
    def test_register_view(self):
        """Test the register endpoint"""
        url = reverse('register')
        data = {
            'phone_number': '5555555555',
            'name': 'New Member',
            'password': 'newpassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        # Verify the user was created
        self.assertTrue(Member.objects.filter(phone_number='5555555555').exists())
    
    def test_login_view(self):
        """Test the login endpoint"""
        url = reverse('login')
        
        # Test valid login
        valid_data = {
            'phone_number': '1234567890',
            'password': 'testpassword'
        }
        response = self.client.post(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        
        # Test invalid credentials
        invalid_data = {
            'phone_number': '1234567890',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test expired subscription
        expired_data = {
            'phone_number': '0987654321',
            'password': 'testpassword'
        }
        response = self.client.post(url, expired_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class GymOperationsTests(APITestCase):
    """
    Test cases for gym operations (enter/exit)
    """
    def setUp(self):
        # Create a test member
        self.member = Member.objects.create_user(
            phone_number="1234567890",
            name="Test Member",
            password="testpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        # Get authentication token
        refresh = RefreshToken.for_user(self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_enter_gym(self):
        """Test the enter gym endpoint"""
        url = reverse('member-enter', args=[self.member.id])
        
        # Test successful entry
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        
        # Refresh member from database
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_in_gym)
        
        # Test already in gym
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_exit_gym(self):
        """Test the exit gym endpoint"""
        # First enter the gym
        self.member.enter_gym()
        
        url = reverse('member-exit', args=[self.member.id])
        
        # Test successful exit
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        
        # Refresh member from database
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_in_gym)
        
        # Test not in gym
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
