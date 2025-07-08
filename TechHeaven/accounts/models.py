from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth import get_user_model

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)  # User must activate account via email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role=models.CharField(max_length=20,choices=(('ADMIN','admin'),('USER','user')),default='USER')
    default_device = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []



#admin invitation
import uuid
from django.utils import timezone

class AdminInvitation(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    admin=models.CharField(max_length=200,null=True,blank=True)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at