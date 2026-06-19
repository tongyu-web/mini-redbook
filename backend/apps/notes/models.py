import uuid
from django.db import models
from config.constants import (
    NOTE_TYPE_IMAGE, NOTE_TYPE_VIDEO, NOTE_STATUS_DRAFT, NOTE_STATUS_PUBLISHED,
    NOTE_STATUS_TAKEN_DOWN, MAX_NOTE_IMAGES, MAX_NOTE_TAGS, MAX_COMMENT_LENGTH,
    NOTE_TYPE_CHOICES, NOTE_STATUS_CHOICES,
)

def uuid4_hex():
    return uuid.uuid4().hex

class Tag(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    name = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=20, blank=True, default="")
    hot_value = models.IntegerField(default=0)
    note_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name

class Note(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="notes", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="")
    type = models.IntegerField(choices=[(NOTE_TYPE_IMAGE, "图文"), (NOTE_TYPE_VIDEO, "视频")], default=NOTE_TYPE_IMAGE)
    cover_img = models.ImageField(upload_to="covers/", blank=True, null=True)
    status = models.IntegerField(choices=[(NOTE_STATUS_DRAFT, "草稿"), (NOTE_STATUS_PUBLISHED, "已发布"), (NOTE_STATUS_TAKEN_DOWN, "下架")], default=NOTE_STATUS_DRAFT)
    category = models.CharField(max_length=20, blank=True, default="")
    like_count = models.IntegerField(default=0)
    fav_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    taken_down_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, through="NoteTag", blank=True)

    class Meta:
        db_table = "notes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class Media(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    note = models.ForeignKey(Note, related_name="media_list", on_delete=models.CASCADE)
    file = models.FileField(upload_to="notes/")
    media_type = models.IntegerField(choices=[(0, "图片"), (1, "视频")], default=0)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "media"
        ordering = ["order"]

class NoteTag(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "note_tags"
        unique_together = [("note", "tag")]

class Comment(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    note = models.ForeignKey(Note, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", related_name="comments", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    content = models.TextField(max_length=MAX_COMMENT_LENGTH)
    image = models.ImageField(upload_to="comments/", blank=True, null=True)
    like_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
