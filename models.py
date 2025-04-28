from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
from django.core.exceptions import ValidationError
import uuid
import re


'''
Documentation:

1. **AccountType Model**:
   - `type`: A unique field to define the type of account.
   - `description`: A text field for additional information about the account type.
   - `is_active`: A boolean to indicate whether the account type is active.
   - `created_at`, `updated_at`: Timestamps for tracking creation and updates.

2. **UserManager**:
   - Custom manager to handle user creation with additional validations.
   - `_validate_password`: Validates password strength.
   - `_create_user`: Handles common user creation logic.
   - `create_user`: Creates a standard user.
   - `create_superuser`: Creates a superuser with elevated permissions.

3. **User Model**:
   - Extends `AbstractBaseUser` and `PermissionsMixin` for custom user functionality.
   - Fields:
     - `email`: Unique identifier for authentication.
     - `username`: Unique username with specific format validations.
     - `first_name`, `last_name`: Personal details of the user.
     - `phone`: Optional phone number with international format validation.
     - `account_type`: ForeignKey to `AccountType` for account categorization.
     - `profile_picture`: Optional user profile image.
     - `bio`: A short biography.
   - Additional Fields:
     - `is_staff`, `is_active`, `date_joined`, `login_attempts`, etc., for user management.
   - Methods:
     - `get_full_name`, `get_short_name`: Utility methods for user details.
   - Custom save method ensures email and username normalization.
'''

class AccountType(models.Model):
    type = models.CharField(max_length=50, unique=True, verbose_name=_("Account Type"), help_text=_("Defines the user's account classification"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Account Type Description"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = _("")
        verbose_name_plural = _("")
        ordering = ['-created_at']

class UserManager(BaseUserManager):
    def _validate_password(self, password):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long"))
        if not re.search(r'\d', password):
            raise ValidationError(_("Password must contain at least one number"))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(_("Password must contain at least one special character"))

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Email must be set'))

        email = self.normalize_email(email)

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            raise ValueError(_('Invalid email format'))

        if password:
            self._validate_password(password)

        is_staff = extra_fields.pop('is_staff', False)
        is_superuser = extra_fields.pop('is_superuser', False)

        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            date_joined=timezone.now(),
            **extra_fields  # Handles other fields like `is_active`
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
from django.utils import timezone
import uuid
import json

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)  # Normal integer-based ID
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # UUID field
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('A valid email address for communication')
    )
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. Use letters, numbers, and @/./+/-/_ only.')
            )
        ]
    )
    first_name = models.CharField(_('first name'), max_length=50, blank=True, validators=[MinLengthValidator(2)])
    last_name = models.CharField(_('last name'), max_length=50, blank=True, validators=[MinLengthValidator(2)])
    phone = models.CharField(
        _("phone"),
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', _('Enter a valid international phone number.'))]
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates administrative access.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates active user status.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    is_locked_out = models.BooleanField(default=False)
    locked_out_until = models.DateTimeField(null=True, blank=True)
    account_type = models.ForeignKey(
        'AccountType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/', null=True, blank=True, max_length=255)
    bio = models.TextField(_('biography'), blank=True, max_length=500)
    failed_attempts = models.JSONField(default=list, blank=True, null=True)  # JSONField to store failed login attempts

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)

    def __str__(self):
        return self.email

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        self.username = self.username.lower().strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']


class AdminUser(User):
    admin_level = models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')], default=1)
    
    class Meta:
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')
    
    def save(self, *args, **kwargs):
        account_type, _ = AccountType.objects.get_or_create(type='Admin')
        self.account_type = account_type
        super().save(*args, **kwargs)


class SEOManager(User):
    managed_domains = models.JSONField(default=list, blank=True)
    report_frequency = models.CharField(
        max_length=20, 
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='weekly'
    )
    
    class Meta:
        verbose_name = _('SEO Manager')
        verbose_name_plural = _('SEO Managers')
    
    def save(self, *args, **kwargs):
        account_type, _ = AccountType.objects.get_or_create(type='SEO Manager')
        self.account_type = account_type
        super().save(*args, **kwargs)







