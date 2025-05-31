from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from ..models import Member, GymSession

class MemberModelTest(TestCase):
    """
    Test cases for the Member model
    """
    def setUp(self):
        # Create a test member with active subscription
        self.active_member = Member.objects.create_user(
            phone_number="1234567890",
            name="Active Member",
            password="testpassword",
            subscription_start=timezone.now().date(),
            subscription_end=timezone.now().date() + timedelta(days=30)
        )
        
        # Create a test member with expired subscription
        self.expired_member = Member.objects.create_user(
            phone_number="0987654321",
            name="Expired Member",
            password="testpassword",
            subscription_start=timezone.now().date() - timedelta(days=60),
            subscription_end=timezone.now().date() - timedelta(days=30)
        )
    
    def test_member_creation(self):
        """Test that members are created correctly"""
        self.assertEqual(self.active_member.name, "Active Member")
        self.assertEqual(self.active_member.phone_number, "1234567890")
        self.assertTrue(self.active_member.check_password("testpassword"))
        
    def test_has_active_subscription(self):
        """Test the has_active_subscription property"""
        self.assertTrue(self.active_member.has_active_subscription)
        self.assertFalse(self.expired_member.has_active_subscription)
        
    def test_enter_gym(self):
        """Test the enter_gym method"""
        # Test successful entry
        success, message = self.active_member.enter_gym()
        self.assertTrue(success)
        self.assertTrue(self.active_member.is_in_gym)
        self.assertIsNotNone(self.active_member.entry_time)
        
        # Test already in gym
        success, message = self.active_member.enter_gym()
        self.assertFalse(success)
        self.assertEqual(message, "Already in the gym")
        
    def test_exit_gym(self):
        """Test the exit_gym method"""
        # First enter the gym
        self.active_member.enter_gym()
        
        # Test successful exit
        success, message = self.active_member.exit_gym()
        self.assertTrue(success)
        self.assertFalse(self.active_member.is_in_gym)
        self.assertIsNone(self.active_member.entry_time)
        
        # Verify a session was created
        self.assertEqual(GymSession.objects.count(), 1)
        session = GymSession.objects.first()
        self.assertEqual(session.member, self.active_member)
        
        # Test exit when not in gym
        success, message = self.active_member.exit_gym()
        self.assertFalse(success)
        self.assertEqual(message, "Not currently in the gym")
        
    def test_str_method(self):
        """Test the string representation of a Member"""
        expected = f"Active Member (1234567890)"
        self.assertEqual(str(self.active_member), expected)


class GymSessionModelTest(TestCase):
    """
    Test cases for the GymSession model
    """
    def setUp(self):
        # Create a test member
        self.member = Member.objects.create_user(
            phone_number="1234567890",
            name="Test Member",
            password="testpassword"
        )
        
        # Create a test gym session
        entry_time = timezone.now() - timedelta(hours=1)
        exit_time = timezone.now()
        duration = (exit_time - entry_time).total_seconds() / 60  # Duration in minutes
        
        self.session = GymSession.objects.create(
            member=self.member,
            entry_time=entry_time,
            exit_time=exit_time,
            duration=duration
        )
    
    def test_session_creation(self):
        """Test that gym sessions are created correctly"""
        self.assertEqual(self.session.member, self.member)
        self.assertAlmostEqual(self.session.duration, 60, delta=1)  # About 60 minutes
        
    def test_str_method(self):
        """Test the string representation of a GymSession"""
        expected = f"{self.member.name} - {self.session.entry_time.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(self.session), expected)
        
    def test_ordering(self):
        """Test that sessions are ordered by entry_time descending"""
        # Create another session with earlier entry time
        earlier_entry = timezone.now() - timedelta(hours=3)
        earlier_exit = timezone.now() - timedelta(hours=2)
        duration = (earlier_exit - earlier_entry).total_seconds() / 60
        
        earlier_session = GymSession.objects.create(
            member=self.member,
            entry_time=earlier_entry,
            exit_time=earlier_exit,
            duration=duration
        )
        
        # Get all sessions and check order
        sessions = GymSession.objects.all()
        self.assertEqual(sessions[0], self.session)  # More recent session first
        self.assertEqual(sessions[1], earlier_session)  # Earlier session second
