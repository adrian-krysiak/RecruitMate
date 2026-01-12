from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserAuthTests(APITestCase):
    """Test suite for user authentication."""
    
    def setUp(self):
        """Set up test data."""
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testPass123!'
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

    def test_user_registration_weak_password(self):
        """Test registration fails with weak password."""
        data = self.user_data.copy()
        data['password'] = '123'
        data['confirm_password'] = '123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_username(self):
        """Test registration fails with duplicate username."""
        User.objects.create_user(
            username='testuser',
            password='testPass123!'
        )
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_with_username(self):
        """Test successful login with username."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        data = {
            'username_email': 'testuser',
            'password': 'testPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)

    def test_user_login_with_email(self):
        """Test successful login with email."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        data = {
            'username_email': 'test@example.com',
            'password': 'testPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        data = {
            'username_email': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_inactive_account(self):
        """Test login fails for inactive user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        user.is_active = False
        user.save()
        
        data = {
            'username_email': 'testuser',
            'password': 'testPass123!'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_email_normalization(self):
        """Test email is normalized to lowercase."""
        data = self.user_data.copy()
        data['email'] = 'Test@EXAMPLE.COM'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_user_logout_success(self):
        """Test successful logout with valid refresh token."""
        # First login to get tokens
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        login_data = {
            'username_email': 'testuser',
            'password': 'testPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh_token']
        access_token = login_response.data['access_token']
        
        # Logout with refresh token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_data = {'refresh_token': refresh_token}
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_user_logout_without_token(self):
        """Test logout fails without refresh token."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        login_data = {
            'username_email': 'testuser',
            'password': 'testPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access_token']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.logout_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_logout_without_authentication(self):
        """Test logout requires authentication."""
        response = self.client.post(self.logout_url, {'refresh_token': 'fake'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_with_refresh_field(self):
        """Test successful logout using 'refresh' field (frontend format)."""
        # First login to get tokens
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testPass123!'
        )
        login_data = {
            'username_email': 'testuser',
            'password': 'testPass123!'
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh_token']
        access_token = login_response.data['access_token']
        
        # Logout with 'refresh' field (as frontend sends it)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_data = {'refresh': refresh_token}  # Using 'refresh' instead of 'refresh_token'
        response = self.client.post(self.logout_url, logout_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
