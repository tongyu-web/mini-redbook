import uuid
from django.db import models

def uuid4_hex():
    return uuid.uuid4().hex

class SearchHistory(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    user = models.ForeignKey("accounts.User", related_name="search_histories", on_delete=models.CASCADE, null=True, blank=True)
    keyword = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "search_histories"
        ordering = ["-created_at"]


class HotSearchTerm(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=uuid4_hex, editable=False)
    keyword = models.CharField(max_length=100, unique=True)
    search_count = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hot_search_terms"
        ordering = ["-search_count"]

    def __str__(self):
        return f"{self.keyword} ({self.search_count})"
