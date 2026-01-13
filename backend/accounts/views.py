import logging
from django.db.models import Q
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (RegisterSerializer, UserDashboardSerializer,
                          UserSerializer, UserLoginSerializer)
from .models import User

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    """Generate access and refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'token_type': 'Bearer',
        'user': UserSerializer(user).data
    }


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.username}")
        return Response(
            get_tokens_for_user(user),
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """User login endpoint supporting username or email."""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_email = serializer.validated_data['username_email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(
                Q(username=username_email) | Q(email=username_email)
            )

            if not user.is_active:
                logger.warning(
                    f"Login attempt for inactive user: {username_email}"
                )
                return Response(
                    {'error': 'Account is disabled.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if user.check_password(password):
                logger.info(f"Successful login: {user.username}")
                return Response(
                    get_tokens_for_user(user),
                    status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            pass

        logger.warning(f"Failed login attempt for: {username_email}")
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """User logout endpoint that blacklists refresh token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Accept both 'refresh' and 'refresh_token' for compatibility
            refresh_token = request.data.get(
                'refresh') or request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User logged out: {request.user.username}")
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            logger.warning(f"Logout failed - invalid token: {str(e)}")
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Logout failed.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDashboardView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint handling GET, PUT, PATCH and DELETE for authenticated user.
    Retrieves and manages the current user's profile.
    """
    serializer_class = UserDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):  # type: ignore
        """Return the authenticated user object."""
        return self.request.user

    def perform_update(self, serializer):
        """Log user profile updates."""
        logger.info(f"User profile updated: {self.request.user.username}")
        serializer.save()

    def perform_destroy(self, instance):
        logger.info(f"User account deleted: {instance.username}")
        instance.delete()
