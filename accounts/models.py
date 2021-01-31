from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

Gender = (
    (1,'Male'),
    (2,'Female'),
    (3,'Other'),
    )
        
        
class User(AbstractBaseUser, PermissionsMixin):
    
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    full_name = models.CharField(_('full name'), max_length=200, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    profile_pic = models.ImageField(blank=True, null=True)
    bio = models.CharField(max_length=400, blank=True)
    website = models.URLField(max_length=400, blank=True)
    phone_no=models.CharField(max_length=12, blank=True)
    gender=models.IntegerField(choices=Gender, blank=True, null=True)
    privacy = models.BooleanField(default=False)
    
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True
        
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)        
        

class ConnectedUsers(models.Model):
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return 'Online Users'
