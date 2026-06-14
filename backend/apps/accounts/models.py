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
    nickname = models.CharField(max_length=MAX_NICKNAME_LENGTH, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(max_length=MAX_BIO_LENGTH, blank=True, default="")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    birthday = models.DateField(blank=True, null=True)
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

    def __str__(self):
        return self.username
