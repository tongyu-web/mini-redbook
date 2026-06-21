import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from config.constants import (
    ACCOUNT_STATUS_NORMAL, ACCOUNT_STATUS_BANNED, ACCOUNT_STATUS_CANCELLED,
    GENDER_UNKNOWN, GENDER_CHOICES, PRIVACY_PUBLIC, MAX_NICKNAME_LENGTH, MAX_BIO_LENGTH,
)

def uuid4_hex():
    return uuid.uuid4().hex

class User(AbstractUser):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    nickname = models.CharField(max_length=MAX_NICKNAME_LENGTH, unique=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(max_length=MAX_BIO_LENGTH, blank=True, default="")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    account_status = models.IntegerField(default=ACCOUNT_STATUS_NORMAL)
    privacy = models.IntegerField(default=PRIVACY_PUBLIC)
    note_count = models.IntegerField(default=0)
    like_received_count = models.IntegerField(default=0)
    fav_received_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    login_fail_count = models.IntegerField(default=0)
    login_locked_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    @property
    def is_profile_complete(self):
        return bool(self.nickname and self.nickname != self.username and self.avatar)

    def __str__(self):
        return self.username

class EmailVerification(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, related_name='email_verifications', on_delete=models.CASCADE, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_verifications'

    def __str__(self):
        return f'{self.email} - {self.code}'


class PhoneVerification(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, related_name='phone_verifications', on_delete=models.CASCADE, null=True, blank=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'phone_verifications'

    def __str__(self):
        return f'{self.phone} - {self.code}'
