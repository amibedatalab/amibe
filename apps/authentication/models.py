from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import os

from apps.authentication.manager import CustomUserManager
from django.utils.translation import gettext_lazy as _
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import EmailMessage

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    uuid = models.UUIDField(blank=True, null=True)
    email=models.EmailField(max_length=100, unique=True,help_text="email should end with @canarahsbclife.in")

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = CustomUserManager()

    class Meta:
        db_table='User'
        verbose_name="User"
        verbose_name_plural="User"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        is_new_user = not self.pk  # Check if the user is being created for the first time
        super().save(*args, **kwargs)  # Call the original save method

        # if is_new_user:
        #     uid = urlsafe_base64_encode(force_bytes(self.pk))
        #     token = default_token_generator.make_token(self)
        #     reset_url = f'http://13.233.156.126/hub/password-reset-confirm/{uid}/{token}/'
        #     from_email = 'noreply.automationhub@canbclife.in'
        #     backend = EmailBackend(
        #         host='smtp.netcorecloud.net',
        #         port='587',
        #         username='rpa1',
        #         password='Canara@5',
        #         use_tls=True,
        #         fail_silently=False
        #     )
        #     msg = EmailMessage(
        #         subject='Password Reset Request (Test Email from Pelocal)',
        #         body=f"Dear User,\n\nYou can reset your password by clicking the following link:\n{reset_url}\n\nIf you did not request this password reset, please ignore this email.",
        #         from_email=f'Support Automation Hub <{from_email}>',
        #         to=[self.username],
        #         connection=backend
        #     )
        #     msg.send(fail_silently=False)


