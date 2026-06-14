from rest_framework import serializers
from .models import Follow, Like, Favorite, FavoriteFolder

class FavoriteFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteFolder
        fields = ["id", "name", "is_public", "note_count", "created_at"]
        read_only_fields = ["id", "note_count", "created_at"]
