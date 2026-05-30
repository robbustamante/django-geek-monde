"""
Alternative implementation of Django's authentication User model,
which allows authentication against the email field in addition to the username.
"""
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def get_by_natural_key(self, username):
        try:
            return self.get(username=username)
        except self.model.DoesNotExist:
            return self.get(is_active=True, email=username)


class User(AbstractUser):
    """
    Alternative implementation of Django's User model allowing authentication
    against the email field in addition to the username field.
    """

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        swappable = 'AUTH_USER_MODEL'

    def get_username(self):
        return self.email

    def __str__(self):
        if self.is_staff or self.is_superuser:
            return self.username
        return self.email or '<anonymous>'

    def get_full_name(self):
        full_name = super().get_full_name()
        if full_name:
            return full_name
        return self.get_short_name()

    def get_short_name(self):
        short_name = super().get_short_name()
        if short_name:
            return short_name
        return self.email

    def validate_unique(self, exclude=None):
        """
        Ensure email uniqueness for active users only.
        Inactive users can't login anyway.
        """
        super().validate_unique(exclude)
        if self.email and self.__class__.objects.exclude(id=self.id).filter(
            is_active=True, email__exact=self.email
        ).exists():
            msg = _('A customer with the e-mail address "{email}" already exists.')
            raise ValidationError({'email': msg.format(email=self.email)})
