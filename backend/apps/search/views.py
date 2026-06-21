from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .tasks import SearchTask
from common.response import ApiResponse
from common.pagination import StandardPagination
from config.constants import NOTE_STATUS_PUBLISHED


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        search_type = request.query_params.get("type", "note")
        page = int(request.query_params.get("page", 1))
        if not q:
            return ApiResponse.error(code=4001, message="请输入搜索关键词", status=400)
        result = SearchTask.search(request.user, q, search_type, page)
        return ApiResponse.success(data=result)


class SuggestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return ApiResponse.success(data=[])
        result = SearchTask.suggest(q)
        return ApiResponse.success(data=result)


class HotTagView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        result = SearchTask.hot_tags()
        return ApiResponse.success(data=result)


class HotSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        result = SearchTask.hot_search_terms(limit=limit)
        return ApiResponse.success(data=result)


class RecommendView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = SearchTask.recommend(request.user)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        from apps.notes.serializers import NoteListSerializer
        ser = NoteListSerializer(page, many=True, context={"request": request})
        return ApiResponse.success(data=paginator.get_paginated_response(ser.data).data)


class SearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import SearchHistory
        qs = SearchHistory.objects.filter(user=request.user).order_by("-created_at")[:20]
        return ApiResponse.success(data=[
            {"id": h.id, "keyword": h.keyword, "created_at": h.created_at.isoformat()}
            for h in qs
        ])

    def delete(self, request):
        from .models import SearchHistory
        keyword = request.data.get("keyword") or request.query_params.get("keyword")
        if keyword:
            SearchHistory.objects.filter(user=request.user, keyword=keyword).delete()
            return ApiResponse.success(message="已删除")
        SearchHistory.objects.filter(user=request.user).delete()
        return ApiResponse.success(message="已清空搜索历史")
