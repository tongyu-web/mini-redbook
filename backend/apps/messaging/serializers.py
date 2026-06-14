from rest_framework import serializers
from .models import Notification, Message

class NotificationSerializer(serializers.ModelSerializer):
    from_user_nickname = serializers.SerializerMethodField()
    from_user_avatar = serializers.SerializerMethodField()
    note_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["id", "to_user", "from_user", "from_user_nickname", "from_user_avatar",
                   "note", "note_title", "comment", "type", "content", "is_read", "created_at"]
        read_only_fields = ["id", "to_user", "created_at"]

    def get_from_user_nickname(self, obj):
        return obj.from_user.nickname if obj.from_user else ""
    def get_from_user_avatar(self, obj):
        if obj.from_user and obj.from_user.avatar and hasattr(obj.from_user.avatar, "url"):
            return obj.from_user.avatar.url
        return ""
    def get_note_title(self, obj):
        return obj.note.title if obj.note else ""

class MessageSerializer(serializers.ModelSerializer):
    from_user_nickname = serializers.SerializerMethodField()
    to_user_nickname = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "from_user", "from_user_nickname", "to_user",
                   "to_user_nickname", "content", "is_read", "created_at"]
        read_only_fields = ["id", "from_user", "is_read", "created_at"]

    def get_from_user_nickname(self, obj):
        return obj.from_user.nickname
    def get_to_user_nickname(self, obj):
        return obj.to_user.nickname
