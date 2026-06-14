from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.utils import timezone
from .models import Note, Comment, Tag
from .serializers import (
    NoteListSerializer, NoteDetailSerializer, NoteCreateSerializer,
    CommentSerializer, TagSerializer
)
from .tasks import NoteTask
from common.response import ApiResponse
from common.permissions import IsOwnerOrReadOnly
from common.pagination import StandardPagination
from config.constants import NOTE_STATUS_PUBLISHED, NOTE_STATUS_DRAFT, RECYCLE_BIN_DAYS

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Note.objects.filter(status=NOTE_STATUS_PUBLISHED).select_related("user").prefetch_related("media_list", "tags")

    def list(self, request):
        qs = self.get_queryset().order_by("-created_at")
        page = self.paginate_queryset(qs)
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=self.get_paginated_response(ser.data).data)

    def create(self, request):
        ser = NoteCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        images = request.FILES.getlist("images") if request.FILES.getlist("images") else None
        video_file = request.FILES.get("video"); video_cover = request.FILES.get("cover_img")
        video = {"file": video_file, "cover": video_cover} if video_file else None
        note = NoteTask.publish_note(request.user, data, images=images, video=video)
        return ApiResponse.success(
            data=NoteDetailSerializer(note, context={"request": request}).data,
            message="发布成功", status=201
        )

    def retrieve(self, request, pk=None):
        note = get_object_or_404(Note, pk=pk, status=NOTE_STATUS_PUBLISHED)
        Note.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        note.refresh_from_db()
        ser = NoteDetailSerializer(note, context={"request": request})
        return ApiResponse.success(data=ser.data)

    def update(self, request, pk=None):
        note = self.get_object()
        ser = NoteCreateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        images = request.FILES.getlist("images") if request.FILES.getlist("images") else None
        NoteTask.edit_note(note, data, images=images)
        ser2 = NoteDetailSerializer(note, context={"request": request})
        return ApiResponse.success(data=ser2.data, message="更新成功")

    def destroy(self, request, pk=None):
        note = self.get_object()
        NoteTask.soft_delete(note)
        return ApiResponse.success(message="已移入回收站")

    @action(detail=False, methods=["get"], url_path="drafts")
    def drafts(self, request):
        qs = Note.objects.filter(user=request.user, status=NOTE_STATUS_DRAFT).order_by("-created_at")
        page = self.paginate_queryset(qs)
        ser = NoteListSerializer(page, many=True)
        return ApiResponse.success(data=self.get_paginated_response(ser.data).data)

    @action(detail=False, methods=["get"], url_path="recycle")
    def recycle(self, request):
        qs = Note.objects.filter(user=request.user, status=2).order_by("-taken_down_at")
        page = self.paginate_queryset(qs)
        ser = NoteListSerializer(page, many=True)
        return ApiResponse.success(data=self.get_paginated_response(ser.data).data)

class NoteRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user, status=2)
        NoteTask.restore_note(note)
        return ApiResponse.success(message="笔记已恢复")

class NoteHardDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if note.status == 2:
            # 从回收站彻底删除
            note.media_list.all().delete()
            note.delete()
            return ApiResponse.success(message="笔记已永久删除")
        # 直接删除已发布笔记
        NoteTask.soft_delete(note)
        return ApiResponse.success(message="已移入回收站")

class RecycleBinCleanupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        deadline = timezone.now() - timezone.timedelta(days=RECYCLE_BIN_DAYS)
        expired = Note.objects.filter(user=request.user, status=2, taken_down_at__lte=deadline)
        count = expired.count()
        for note in expired:
            note.media_list.all().delete()
        expired.delete()
        return ApiResponse.success(data={"cleaned_count": count}, message=f"已清理{count}条过期笔记")

class UserNoteListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, user_id):
        qs = Note.objects.filter(user_id=user_id, status=NOTE_STATUS_PUBLISHED).order_by("-created_at")
        paginator = StandardPagination(); page = paginator.paginate_queryset(qs, request)
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

class LikedNoteListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        from apps.social.models import Like
        note_ids = Like.objects.filter(user=request.user).values_list("note_id", flat=True)
        qs = Note.objects.filter(id__in=list(note_ids), status=NOTE_STATUS_PUBLISHED).order_by("-created_at")
        paginator = StandardPagination(); page = paginator.paginate_queryset(qs, request)
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

class DraftListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Note.objects.filter(user=request.user, status=NOTE_STATUS_DRAFT).order_by("-updated_at")
        ser = NoteListSerializer(qs, many=True); return ApiResponse.success(data=ser.data)
    def delete(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user, status=NOTE_STATUS_DRAFT)
        note.delete(); return ApiResponse.success(message="草稿已删除")

class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, note_id):
        qs = Comment.objects.filter(note_id=note_id, parent=None).select_related("user").prefetch_related("replies__user")
        paginator = StandardPagination(); page = paginator.paginate_queryset(qs, request)
        ser = CommentSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)
    def post(self, request, note_id):
        note = get_object_or_404(Note, pk=note_id, status=NOTE_STATUS_PUBLISHED)
        content = request.data.get("content", "").strip()
        if not content: return ApiResponse.error(code=4001, message="评论内容不能为空", status=400)
        comment = Comment.objects.create(note=note, user=request.user, content=content,
            parent_id=request.data.get("parent_id") or None)
        Note.objects.filter(pk=note_id).update(comment_count=F("comment_count") + 1)
        ser = CommentSerializer(comment, context={"request": request})
        return ApiResponse.success(data=ser.data, message="评论成功", status=201)

class TagListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request):
        tags = Tag.objects.all().order_by("-hot_value"); ser = TagSerializer(tags, many=True)
        return ApiResponse.success(data=ser.data)
    def post(self, request):
        name = request.data.get("name", "").strip()
        if not name: return ApiResponse.error(code=4001, message="标签名不能为空", status=400)
        tag, _ = Tag.objects.get_or_create(name=name)
        return ApiResponse.success(data=TagSerializer(tag).data, status=201)
