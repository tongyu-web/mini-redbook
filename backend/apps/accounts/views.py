from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if User.objects.filter(username=data["username"]).exists():
            return ApiResponse.error(code=4001, message="用户名已存在", status=409)
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            nickname=data.get("nickname", data["username"]),
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
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        target_id = user_id or request.user.id
        try:
            user = User.objects.get(id=target_id)
        except User.DoesNotExist:
            return ApiResponse.error(code=4004, message="用户不存在", status=404)
        ser = UserProfileSerializer(user, context={"request": request})
        return ApiResponse.success(data=ser.data)

    def put(self, request):
        ser = UserUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        for key, value in ser.validated_data.items():
            setattr(request.user, key, value)
        request.user.save()
        return ApiResponse.success(data=UserProfileSerializer(request.user).data, message="更新成功")

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if "avatar" not in request.FILES:
            return ApiResponse.error(code=4001, message="请上传图片", status=400)
        request.user.avatar = request.FILES["avatar"]
        request.user.save()
        return ApiResponse.success(data={"avatar_url": request.user.avatar.url if request.user.avatar else ""}, message="上传成功")

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
