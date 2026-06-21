from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import serializers as drf_serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, UserSimpleSerializer
)
from .tasks import AccountTask
from common.response import ApiResponse
from common.pagination import StandardPagination
from config.constants import MAX_AVATAR_SIZE_MB

ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png", "image/jpg"]

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if User.objects.filter(username=data["username"]).exists():
            return ApiResponse.error(code=4001, message="用户名已存在", status=409)
        nickname = data.get("nickname", "").strip() or data["username"]
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            nickname=nickname,
            gender=data.get("gender", "UNKNOWN")
        )
        refresh = RefreshToken.for_user(user)
        return ApiResponse.success(data={
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": UserProfileSerializer(user).data
        }, message="注册成功", status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            user = User.objects.get(username=data["username"])
        except User.DoesNotExist:
            return ApiResponse.error(code=4001, message="用户名或密码错误", status=401)
        if user.login_locked_until and user.login_locked_until > timezone.now():
            return ApiResponse.error(code=4001, message="账号已锁定，请稍后再试", status=423)
        if not user.check_password(data["password"]):
            AccountTask.handle_login_fail(user)
            return ApiResponse.error(code=4001, message="用户名或密码错误", status=401)
        AccountTask.handle_login_success(user)
        refresh = RefreshToken.for_user(user)
        return ApiResponse.success(data={
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": UserProfileSerializer(user).data
        }, message="登录成功")

class ProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id=None):
        target_id = user_id or request.user.id
        try:
            user = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return ApiResponse.error(code=4004, message="用户不存在", status=404)
        ser = UserProfileSerializer(user, context={"request": request})
        return ApiResponse.success(data=ser.data)

    def put(self, request):
        ser = UserUpdateSerializer(data=request.data, partial=True, context={"request": request})
        ser.is_valid(raise_exception=True)
        for key, value in ser.validated_data.items():
            setattr(request.user, key, value)
        request.user.save()
        return ApiResponse.success(data=UserProfileSerializer(request.user).data, message="更新成功")

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if "avatar" not in request.FILES:
            return ApiResponse.error(code=4001, message="请选择头像图片", status=400)
        avatar = request.FILES["avatar"]
        if avatar.content_type not in ALLOWED_AVATAR_TYPES:
            return ApiResponse.error(code=4001, message="仅支持 JPG/PNG 格式", status=400)
        if avatar.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
            return ApiResponse.error(code=4001, message=f"头像大小不能超过{MAX_AVATAR_SIZE_MB}MB", status=400)
        request.user.avatar = avatar
        request.user.save()
        return ApiResponse.success(data={"avatar_url": request.user.avatar.url if request.user.avatar else ""}, message="头像上传成功")

class ProfileStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        missing = []
        if not request.user.nickname or request.user.nickname == request.user.username:
            missing.append("nickname")
        if not request.user.avatar:
            missing.append("avatar")
        if not request.user.bio:
            missing.append("bio")
        if request.user.gender == "UNKNOWN":
            missing.append("gender")
        return ApiResponse.success(data={
            "is_complete": len(missing) == 0,
            "missing_fields": missing,
            "completion_percent": max(0, 100 - len(missing) * 25)
        })

class FollowPagination(StandardPagination):
    page_size = 20

class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        from apps.social.models import Follow
        user_ids = Follow.objects.filter(following_id=user_id).values_list("follower_id", flat=True)
        users = User.objects.filter(id__in=user_ids)
        paginator = FollowPagination()
        page = paginator.paginate_queryset(users, request)
        ser = UserSimpleSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

class ChangePasswordView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_pw = request.data.get("old_password", "")
        new_pw = request.data.get("new_password", "")
        if not old_pw or not new_pw:
            return ApiResponse.error(code=4001, message="请填写旧密码和新密码", status=400)
        if len(new_pw) < 6:
            return ApiResponse.error(code=4001, message="新密码至少6位", status=400)
        if not request.user.check_password(old_pw):
            return ApiResponse.error(code=4001, message="旧密码不正确", status=400)
        request.user.set_password(new_pw)
        request.user.save()
        return ApiResponse.success(message="密码修改成功")


class BindEmailView(APIView):
    """绑定/换绑邮箱"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return ApiResponse.error(code=4001, message="请输入邮箱", status=400)
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            return ApiResponse.error(code=4001, message="该邮箱已被绑定", status=409)
        request.user.email = email
        request.user.save()
        return ApiResponse.success(data={"email": email}, message="邮箱绑定成功")


class CancelAccountView(APIView):
    """注销账号（需二次确认+填写原因）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reason = request.data.get("reason", "").strip()
        password = request.data.get("password", "")
        if not password:
            return ApiResponse.error(code=4001, message="请输入密码确认注销", status=400)
        if not request.user.check_password(password):
            return ApiResponse.error(code=4001, message="密码不正确", status=400)
        request.user.account_status = 2
        request.user.is_active = False
        request.user.save()
        return ApiResponse.success(message="账号已注销")


class PrivacySettingsView(APIView):
    """隐私设置：0公开/1仅好友/2私密"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        privacy = request.data.get("privacy")
        if privacy not in [0, 1, 2]:
            return ApiResponse.error(code=4001, message="隐私设置无效（0:公开 1:好友 2:私密）", status=400)
        request.user.privacy = privacy
        request.user.save()
        return ApiResponse.success(data={"privacy": privacy}, message="隐私设置已更新")

class LogoutView(APIView):
    """退出登录（黑名单当前 refresh token）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = request.data.get("refresh", "")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return ApiResponse.success(message="已退出登录")

class SendEmailCodeView(APIView):
    """发送邮箱验证码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return ApiResponse.error(code=4001, message="请输入邮箱地址", status=400)
        import random
        code = "".join(random.choices("0123456789", k=6))
        from .models import EmailVerification
        EmailVerification.objects.filter(email=email, is_used=False).update(is_used=True)
        EmailVerification.objects.create(email=email, code=code, user=request.user)
        from django.core.mail import send_mail
        from django.conf import settings
        try:
            send_mail(
                subject="Mini小红书 - 邮箱验证码",
                message=f"您的验证码是：{code}\n验证码有效期为10分钟，请勿泄露给他人。",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return ApiResponse.success(data={"email": email}, message="验证码已发送")
        except Exception as e:
            return ApiResponse.error(code=5001, message=f"邮件发送失败: {str(e)}", status=500)


class BindEmailWithCodeView(APIView):
    """验证码绑定邮箱"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email", "").strip()
        code = request.data.get("code", "").strip()
        if not email or not code:
            return ApiResponse.error(code=4001, message="请填写邮箱和验证码", status=400)
        from .models import EmailVerification
        from django.utils import timezone
        from datetime import timedelta
        record = EmailVerification.objects.filter(
            email=email, code=code, is_used=False,
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).first()
        if not record:
            return ApiResponse.error(code=4001, message="验证码无效或已过期", status=400)
        from .models import User
        # If another user has this email, auto-unbind since current user proved ownership
        User.objects.filter(email=email).exclude(id=request.user.id).update(email="")
        record.is_used = True
        record.save()
        request.user.email = email
        request.user.save()
        return ApiResponse.success(data={"email": email}, message="邮箱绑定成功")

class UnbindEmailView(APIView):
    """解绑邮箱"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.email:
            return ApiResponse.error(code=4001, message="当前未绑定邮箱", status=400)
        request.user.email = ""
        request.user.save()
        return ApiResponse.success(message="邮箱已解绑")

class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        from apps.social.models import Follow
        user_ids = Follow.objects.filter(follower_id=user_id).values_list("following_id", flat=True)
        users = User.objects.filter(id__in=user_ids)
        paginator = FollowPagination()
        page = paginator.paginate_queryset(users, request)
        ser = UserSimpleSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

class ChangePasswordView(APIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_pw = request.data.get("old_password", "")
        new_pw = request.data.get("new_password", "")
        if not old_pw or not new_pw:
            return ApiResponse.error(code=4001, message="请填写旧密码和新密码", status=400)
        if len(new_pw) < 6:
            return ApiResponse.error(code=4001, message="新密码至少6位", status=400)
        if not request.user.check_password(old_pw):
            return ApiResponse.error(code=4001, message="旧密码不正确", status=400)
        request.user.set_password(new_pw)
        request.user.save()
        return ApiResponse.success(message="密码修改成功")


class BindEmailView(APIView):
    """绑定/换绑邮箱"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return ApiResponse.error(code=4001, message="请输入邮箱", status=400)
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            return ApiResponse.error(code=4001, message="该邮箱已被绑定", status=409)
        request.user.email = email
        request.user.save()
        return ApiResponse.success(data={"email": email}, message="邮箱绑定成功")


class CancelAccountView(APIView):
    """注销账号（需二次确认+填写原因）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reason = request.data.get("reason", "").strip()
        password = request.data.get("password", "")
        if not password:
            return ApiResponse.error(code=4001, message="请输入密码确认注销", status=400)
        if not request.user.check_password(password):
            return ApiResponse.error(code=4001, message="密码不正确", status=400)
        request.user.account_status = 2
        request.user.is_active = False
        request.user.save()
        return ApiResponse.success(message="账号已注销")


class PrivacySettingsView(APIView):
    """隐私设置：0公开/1仅好友/2私密"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        privacy = request.data.get("privacy")
        if privacy not in [0, 1, 2]:
            return ApiResponse.error(code=4001, message="隐私设置无效（0:公开 1:好友 2:私密）", status=400)
        request.user.privacy = privacy
        request.user.save()
        return ApiResponse.success(data={"privacy": privacy}, message="隐私设置已更新")

class LogoutView(APIView):
    """退出登录（黑名单当前 refresh token）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = request.data.get("refresh", "")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return ApiResponse.success(message="已退出登录")
