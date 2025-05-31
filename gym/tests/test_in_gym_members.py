from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from ..models import Member

class InGymMembersViewTest(TestCase):
    """
    Test cases for the InGymMembersView endpoint
    """
    def setUp(self):
        # Create an admin user
        self.admin = Member.objects.create_user(
            phone_number="9999999999",
            name="Admin User",
            password="adminpassword",
            is_staff=True
        )
        
        # Create a regular user with active subscription
        self.regular_user = Member.objects.create_user(
            phone_number="1234567890",
            name="Regular User",
            password="userpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        # Create a user with expired subscription
        self.expired_user = Member.objects.create_user(
            phone_number="5555555555",
            name="Expired User",
            password="expiredpassword",
            subscription_start=timezone.now().date() - timedelta(days=60),
            subscription_end=timezone.now().date() - timedelta(days=30)
        )
        
        # Create some members with different gym statuses
        self.in_gym_member1 = Member.objects.create_user(
            phone_number="1111111111",
            name="In Gym Member 1",
            password="password",
            is_in_gym=True,
            entry_time=timezone.now(),
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        self.in_gym_member2 = Member.objects.create_user(
            phone_number="2222222222",
            name="In Gym Member 2",
            password="password",
            is_in_gym=True,
            entry_time=timezone.now(),
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        self.not_in_gym_member = Member.objects.create_user(
            phone_number="3333333333",
            name="Not In Gym Member",
            password="password",
            is_in_gym=False,
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        self.client = APIClient()
    
    def test_in_gym_members_admin_access(self):
        """Test that admin users can access the in-gym members endpoint"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('members-in-gym')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['members']), 2)
        
        # Check that only in-gym members are returned
        member_ids = [member['id'] for member in response.data['members']]
        self.assertIn(self.in_gym_member1.id, member_ids)
        self.assertIn(self.in_gym_member2.id, member_ids)
        self.assertNotIn(self.not_in_gym_member.id, member_ids)
    
    def test_in_gym_members_regular_user_access(self):
        """Test that regular users with active subscription can access the in-gym members endpoint"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('members-in-gym')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Check that only in-gym members are returned
        member_ids = [member['id'] for member in response.data['members']]
        self.assertIn(self.in_gym_member1.id, member_ids)
        self.assertIn(self.in_gym_member2.id, member_ids)
        self.assertNotIn(self.not_in_gym_member.id, member_ids)
    
    def test_in_gym_members_expired_user_access(self):
        """Test that users with expired subscription cannot access the in-gym members endpoint"""
        self.client.force_authenticate(user=self.expired_user)
        url = reverse('members-in-gym')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_in_gym_members_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the in-gym members endpoint"""
        url = reverse('members-in-gym')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
