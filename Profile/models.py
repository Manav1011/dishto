from django.db import models
from django.contrib.auth.models import User,AbstractUser
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from dishto.GlobalUtils import generate_unique_hash,normalize_email


# Create your models here.
# In settings.py AUTH_USER_MODEL = 'yourapp.CustomUserModel'

class Profile(AbstractUser):
    ROLE_CHOICES = [
        ('franchise_owner', 'Frachise Owner'),
        ('outlet_owner', 'Outlet Owner'),
    ]
    username = None
    name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(_('email address'),unique=True,null=True,blank=True)
    ph_no = models.CharField(max_length=20,null=True,blank=True)
    role = models.CharField(max_length=128, choices=ROLE_CHOICES)    
    slug = models.SlugField(unique=True, null=True, blank=True)
    forgot_password_code = models.SlugField(null=True, blank=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email if self.email else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        if not self.forgot_password_code:
            self.forgot_password_code = generate_unique_hash()
        self.email = normalize_email(self.email)
        super(Profile, self).save(*args, **kwargs)