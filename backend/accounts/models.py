from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser."""

    # Override email to make it unique and required
    email = models.EmailField(unique=True, blank=False)

    # Custom fields
    birth_date = models.DateField(null=True, blank=True)
    is_premium = models.BooleanField(default=True)

    # Email is required for registration
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
