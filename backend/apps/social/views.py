from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import Like, Favorite, FavoriteFolder, Follow
from .serializers import FavoriteFolderSerializer
from .tasks import SocialTask
from common.response import ApiResponse
from common.pagination import StandardPagination
import logging
import traceback
logger = logging.getLogger(__name__)


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        result = SocialTask.follow_user(request.user, user_id)
        if result is None:
            return ApiResponse.error(code=4001, message="不能关注自己", status=400)
        return ApiResponse.success(data=result, message="操作成功")

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, note_id):
        try:
            result = SocialTask.toggle_like(request.user, note_id)
            return ApiResponse.success(data=result)
        except Exception as e:
            logger.error("LikeView error for note %s: %s\n%s", note_id, e, traceback.format_exc())
            return ApiResponse.error(code=5001, message=f"点赞失败: {str(e)}", status=500)

class FavoriteFolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteFolderSerializer
    pagination_class = None

    def get_queryset(self):
        return FavoriteFolder.objects.filter(user=self.request.user)

    def list(self, request):
        qs = self.get_queryset()
        ser = self.get_serializer(qs, many=True)
        return ApiResponse.success(data=ser.data)

    def create(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        self.perform_create(ser)
        return ApiResponse.success(data=ser.data, status=201)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        from apps.notes.models import Note
        favs = instance.favorites.all()
        for fav in favs:
            Note.objects.filter(pk=fav.note_id).update(fav_count=F("fav_count") - 1)
        instance.delete()

class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            note_id = request.data.get("note_id")
            folder_id = request.data.get("folder_id", "")
            if not note_id:
                return ApiResponse.error(code=4001, message="缺少 note_id", status=400)
            if not folder_id:
                folder, _ = FavoriteFolder.objects.get_or_create(user=request.user, name="默认收藏夹")
                folder_id = folder.id
            result = SocialTask.add_to_favorite(request.user, note_id, folder_id)
            return ApiResponse.success(data=result)
        except Exception as e:
            logger.error("FavoriteView.post error: %s\n%s", e, traceback.format_exc())
            return ApiResponse.error(code=5001, message=f"收藏失败: {str(e)}", status=500)

    def delete(self, request):
        try:
            note_id = request.data.get("note_id")
            folder_id = request.data.get("folder_id")
            if not note_id or not folder_id:
                return ApiResponse.error(code=4001, message="缺少参数", status=400)
            result = SocialTask.remove_from_favorite(request.user, note_id, folder_id)
            return ApiResponse.success(data=result)
        except Exception as e:
            logger.error("FavoriteView.delete error: %s\n%s", e, traceback.format_exc())
            return ApiResponse.error(code=5001, message=f"取消收藏失败: {str(e)}", status=500)

    def get(self, request, folder_id):
        folder = get_object_or_404(FavoriteFolder, pk=folder_id, user=request.user)
        from apps.notes.models import Note
        note_ids = Favorite.objects.filter(folder=folder).values_list("note_id", flat=True)
        qs = Note.objects.filter(id__in=list(note_ids))
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        from apps.notes.serializers import NoteListSerializer
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

class FavoriteAllView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        note_ids = Favorite.objects.filter(user=request.user).values_list("note_id", flat=True).distinct()
        from apps.notes.models import Note
        qs = Note.objects.filter(id__in=list(note_ids))
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        from apps.notes.serializers import NoteListSerializer
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)


class RemoveFollowerView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        from .models import Follow
        Follow.objects.filter(follower_id=user_id, following=request.user).delete()
        from apps.accounts.models import User
        User.objects.filter(id=user_id).update(following_count=F("following_count") - 1)
        User.objects.filter(id=request.user.id).update(follower_count=F("follower_count") - 1)
        return ApiResponse.success(message="已移除粉丝")

class FavoriteRemoveAllView(APIView):
    """从所有收藏夹中移除某篇笔记"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, note_id):
        from .models import Favorite
        from apps.notes.models import Note
        from django.db.models import F
        favs = Favorite.objects.filter(user=request.user, note_id=note_id)
        count = favs.count()
        if count > 0:
            Note.objects.filter(pk=note_id).update(fav_count=F("fav_count") - 1)
            for fav in favs:
                from .models import FavoriteFolder
                FavoriteFolder.objects.filter(pk=fav.folder_id).update(note_count=F("note_count") - 1)
            favs.delete()
            from apps.accounts.models import User
            User.objects.filter(id=Note.objects.get(pk=note_id).user_id).update(fav_received_count=F("fav_received_count") - 1)
        return ApiResponse.success(data={"is_favorited": False, "removed_count": count})
