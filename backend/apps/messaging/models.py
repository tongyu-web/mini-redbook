import uuid
from django.db import models
from config.constants import NOTIFICATION_TYPE_CHOICES, NOTIFICATION_TYPE_LIKE

def uuid4_hex():
    return uuid.uuid4().hex

class Notification(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    to_user = models.ForeignKey("accounts.User", related_name="notifications", on_delete=models.CASCADE)
    from_user = models.ForeignKey("accounts.User", related_name="sent_notifications", on_delete=models.CASCADE, null=True, blank=True)
    note = models.ForeignKey("notes.Note", on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey("notes.Comment", on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default=NOTIFICATION_TYPE_LIKE)
    content = models.TextField(blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

class Message(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    from_user = models.ForeignKey("accounts.User", related_name="sent_messages", on_delete=models.CASCADE)
    to_user = models.ForeignKey("accounts.User", related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

class BlockedContact(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="blocked_contacts", on_delete=models.CASCADE)
    blocked_user = models.ForeignKey("accounts.User", related_name="blocked_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blocked_contacts"
        unique_together = [("user", "blocked_user")]
