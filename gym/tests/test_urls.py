from django.test import TestCase
from django.urls import reverse, resolve
from .. import views

class URLTests(TestCase):
    """
    Test cases for URL routing
    """
    
    def test_register_url(self):
        """Test the register URL"""
        url = reverse('register')
        self.assertEqual(url, '/api/register/')
        self.assertEqual(resolve(url).func.view_class, views.RegisterView)
    
    def test_login_url(self):
        """Test the login URL"""
        url = reverse('login')
        self.assertEqual(url, '/api/login/')
        self.assertEqual(resolve(url).func.view_class, views.LoginView)
    
    def test_member_list_url(self):
        """Test the member list URL"""
        url = reverse('member-list')
        self.assertEqual(url, '/api/members/')
        self.assertEqual(resolve(url).func.view_class, views.MemberListView)
    
    def test_member_detail_url(self):
        """Test the member detail URL"""
        url = reverse('member-detail', args=[1])
        self.assertEqual(url, '/api/members/1/')
        self.assertEqual(resolve(url).func.view_class, views.MemberDetailView)
    
    def test_member_enter_url(self):
        """Test the member enter gym URL"""
        url = reverse('member-enter', args=[1])
        self.assertEqual(url, '/api/members/1/enter/')
        self.assertEqual(resolve(url).func.view_class, views.MemberEnterGymView)
    
    def test_member_exit_url(self):
        """Test the member exit gym URL"""
        url = reverse('member-exit', args=[1])
        self.assertEqual(url, '/api/members/1/exit/')
        self.assertEqual(resolve(url).func.view_class, views.MemberExitGymView)
    
    def test_session_list_url(self):
        """Test the session list URL"""
        url = reverse('session-list')
        self.assertEqual(url, '/api/sessions/')
        self.assertEqual(resolve(url).func.view_class, views.GymSessionListView)
