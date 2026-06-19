from rest_framework import serializers
from .models import Note, Tag, Media, NoteTag, Comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "file", "media_type", "order"]

class NoteListSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ["id", "title", "cover_img", "like_count", "fav_count",
                   "comment_count", "view_count", "type", "type_label",
                   "user_nickname", "user_avatar", "category", "created_at"]

    def get_user_nickname(self, obj):
        return obj.user.nickname

    def get_user_avatar(self, obj):
        if obj.user.avatar and hasattr(obj.user.avatar, "url"):
            return obj.user.avatar.url
        return ""

    def get_type_label(self, obj):
        return "视频" if obj.type == 1 else "图文"

class NoteDetailSerializer(serializers.ModelSerializer):
    media_list = MediaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user_nickname = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ["id", "title", "content", "type", "type_label", "cover_img", "status",
                   "like_count", "fav_count", "comment_count", "view_count",
                   "is_edited", "media_list", "tags", "user_nickname",
                   "user_avatar", "user_id", "is_liked", "is_favorited",
                   "category", "created_at", "updated_at"]

    def get_user_nickname(self, obj):
        return obj.user.nickname
    def get_user_avatar(self, obj):
        if obj.user.avatar and hasattr(obj.user.avatar, "url"):
            return obj.user.avatar.url
        return ""
    def get_user_id(self, obj):
        return obj.user_id
    def get_type_label(self, obj):
        return "视频" if obj.type == 1 else "图文"
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from apps.social.models import Like
            return Like.objects.filter(user=request.user, note=obj).exists()
        return False
    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from apps.social.models import Favorite
            return Favorite.objects.filter(user=request.user, note=obj).exists()
        return False

class NoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=[0, 1], required=False, default=0)
    tag_ids = serializers.ListField(child=serializers.CharField(), required=False, max_length=8)
    tag_names = serializers.ListField(child=serializers.CharField(max_length=30), required=False, max_length=8)
    category = serializers.CharField(max_length=20, required=False, default="")

    def validate_images(self, files):
        if len(files) > 8:
            raise serializers.ValidationError("最多上传8张图片")
        return files

    def validate_video(self, file):
        max_size = 500 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError("视频文件不能超过500MB")
        return file

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    user_nickname = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "note", "user", "parent", "content", "image",
                   "like_count", "created_at", "replies", "user_nickname", "user_avatar"]
        read_only_fields = ["id", "user", "like_count", "created_at"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data if replies else []

    def get_user_nickname(self, obj):
        return obj.user.nickname
    def get_user_avatar(self, obj):
        if obj.user.avatar and hasattr(obj.user.avatar, "url"):
            return obj.user.avatar.url
        return ""
