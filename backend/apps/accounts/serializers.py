from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    nickname = serializers.CharField(max_length=15, required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=["MALE","FEMALE","UNKNOWN"], required=False)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    is_profile_complete = serializers.BooleanField(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "nickname", "avatar_url", "bio", "gender",
                   "birthday", "note_count", "like_received_count", "fav_received_count",
                   "follower_count", "following_count", "privacy", "created_at",
                   "is_profile_complete", "is_following"]

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            return obj.avatar.url
        return ""
    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated and str(request.user.id) != str(obj.id):
            from apps.social.models import Follow
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

class UserUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=15, required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=["MALE","FEMALE","UNKNOWN"], required=False)
    birthday = serializers.DateField(required=False)
    privacy = serializers.IntegerField(required=False)

    def validate_nickname(self, value):
        qs = User.objects.filter(nickname=value)
        if self.context.get("request") and hasattr(self.context["request"], "user"):
            qs = qs.exclude(id=self.context["request"].user.id)
        if qs.exists():
            raise serializers.ValidationError("该昵称已被使用")
        return value

class UserSimpleSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "nickname", "avatar_url", "bio", "note_count",
                   "follower_count", "following_count", "is_following",
                   "is_profile_complete"]

    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, "url"):
            return obj.avatar.url
        return ""

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from apps.social.models import Follow
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False
