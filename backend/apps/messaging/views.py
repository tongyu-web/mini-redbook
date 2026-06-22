from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from apps.accounts.models import User
from .models import Notification, Message, BlockedContact
from .serializers import NotificationSerializer, MessageSerializer
from common.response import ApiResponse
from common.pagination import StandardPagination

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user).select_related("from_user", "note")

    def list(self, request):
        qs = self.get_queryset()
        ntype = request.query_params.get("type")
        if ntype:
            qs = qs.filter(type=ntype)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        ser = self.get_serializer(page, many=True)
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

    def partial_update(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return ApiResponse.success(data=self.get_serializer(notification).data)

class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(to_user=request.user, is_read=False)
        total = qs.count()
        by_type = {}
        for nt in ["like", "comment", "follow", "favorite", "comment_like", "message"]:
            by_type[nt] = qs.filter(type=nt).count()
        # Also count unread private messages (from Message model)
        unread_msg_count = Message.objects.filter(to_user=request.user, is_read=False).count()
        return ApiResponse.success(data={
            "unread_count": total,
            "by_type": by_type,
            "unread_message_count": unread_msg_count,
        })

class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(to_user=request.user, is_read=False).update(is_read=True)
        return ApiResponse.success(message="全部已读")

class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        last_msgs = Message.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).values("from_user", "to_user").annotate(last_time=Max("created_at")).order_by("-last_time")

        seen = set()
        conversations = []
        for msg in last_msgs:
            other_id = str(msg["from_user"]) if str(msg["from_user"]) != str(user.id) else str(msg["to_user"])
            if other_id in seen:
                continue
            seen.add(other_id)
            last = Message.objects.filter(
                Q(from_user=user, to_user_id=other_id) | Q(from_user_id=other_id, to_user=user)
            ).order_by("-created_at").first()
            unread = Message.objects.filter(from_user_id=other_id, to_user=user, is_read=False).count()
            try:
                other_user = User.objects.get(id=other_id)
            except User.DoesNotExist:
                continue
            conversations.append({
                "user_id": other_id,
                "nickname": other_user.nickname,
                "avatar_url": other_user.avatar.url if other_user.avatar else "",
                "last_message": last.content if last else "",
                "last_time": last.created_at.strftime("%Y-%m-%d %H:%M") if last else "",
                "unread_count": unread,
            })
        return ApiResponse.success(data=conversations)

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        qs = Message.objects.filter(
            Q(from_user=request.user, to_user_id=user_id) | Q(from_user_id=user_id, to_user=request.user)
        ).order_by("created_at")
        qs.filter(from_user_id=user_id, to_user=request.user, is_read=False).update(is_read=True)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        ser = MessageSerializer(page, many=True)
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)

    def post(self, request):
        to_user_id = request.data.get("to_user_id")
        content = request.data.get("content", "").strip()
        if not to_user_id or not content:
            return ApiResponse.error(code=4001, message="参数不完整", status=400)
        if BlockedContact.objects.filter(user_id=to_user_id, blocked_user=request.user).exists():
            return ApiResponse.error(code=4001, message="对方已屏蔽你", status=403)
        msg = Message.objects.create(from_user=request.user, to_user_id=to_user_id, content=content)
        return ApiResponse.success(data=MessageSerializer(msg).data, message="发送成功", status=201)

class BlockContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        BlockedContact.objects.get_or_create(user=request.user, blocked_user_id=user_id)
        return ApiResponse.success(message="已屏蔽")

    def delete(self, request, user_id):
        BlockedContact.objects.filter(user=request.user, blocked_user_id=user_id).delete()
        return ApiResponse.success(message="已取消屏蔽")

class DeleteConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        Message.objects.filter(
            Q(from_user=request.user, to_user_id=user_id) | Q(from_user_id=user_id, to_user=request.user)
        ).delete()
        return ApiResponse.success(message="会话已删除")

