import uuid
from django.db import models

def uuid4_hex():
    return uuid.uuid4().hex

class Follow(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    follower = models.ForeignKey("accounts.User", related_name="following_set", on_delete=models.CASCADE)
    following = models.ForeignKey("accounts.User", related_name="follower_set", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follows"
        unique_together = [("follower", "following")]

    def __str__(self):
        return f"{self.follower_id} -> {self.following_id}"

class Like(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="likes", on_delete=models.CASCADE)
    note = models.ForeignKey("notes.Note", related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "likes"
        unique_together = [("user", "note")]

class FavoriteFolder(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="favorite_folders", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_public = models.BooleanField(default=True)
    note_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorite_folders"

class Favorite(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="favorites", on_delete=models.CASCADE)
    note = models.ForeignKey("notes.Note", related_name="favorites", on_delete=models.CASCADE)
    folder = models.ForeignKey(FavoriteFolder, related_name="favorites", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorites"
        unique_together = [("user", "note", "folder")]
