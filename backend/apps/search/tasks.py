from django.db.models import Q
from .models import SearchHistory
from config.constants import NOTE_STATUS_PUBLISHED, MAX_SEARCH_HISTORY, ACCOUNT_STATUS_NORMAL

class SearchTask:
    @staticmethod
    def search(user, keyword, search_type, page=1, page_size=20):
        if user and user.is_authenticated:
            SearchHistory.objects.create(user=user, keyword=keyword)
            total = SearchHistory.objects.filter(user=user).count()
            if total > MAX_SEARCH_HISTORY:
                ids = SearchHistory.objects.filter(user=user).values_list("id", flat=True)[MAX_SEARCH_HISTORY:]
                SearchHistory.objects.filter(id__in=list(ids)).delete()

        from apps.notes.models import Note
        from apps.accounts.models import User
        from apps.notes.models import Tag

        if search_type == "note":
            qs = Note.objects.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword),
                status=NOTE_STATUS_PUBLISHED
            ).order_by("-created_at")
        elif search_type == "user":
            qs = User.objects.filter(
                nickname__icontains=keyword,
                account_status=ACCOUNT_STATUS_NORMAL
            )
        elif search_type == "tag":
            qs = Tag.objects.filter(name__icontains=keyword)
        else:
            qs = Note.objects.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword),
                status=NOTE_STATUS_PUBLISHED
            ).order_by("-created_at")

        from common.pagination import StandardPagination
        paginator = StandardPagination()
        paginator.page_size = page_size
        page_obj = paginator.paginate_queryset(qs, type("Req", (), {"query_params": {"page": str(page), "page_size": str(page_size)}})())
        return paginator.get_paginated_response(page_obj).data if hasattr(paginator, "get_paginated_response") else {}

    @staticmethod
    def suggest(prefix):
        from apps.notes.models import Tag
        return list(Tag.objects.filter(name__istartswith=prefix).order_by("-hot_value")[:10].values("name", "hot_value"))

    @staticmethod
    def hot_tags():
        from apps.notes.models import Tag
        return list(Tag.objects.order_by("-hot_value")[:20].values("name", "hot_value", "note_count"))

    @staticmethod
    def recommend(user):
        from apps.notes.models import Note, NoteTag, Tag
        from config.constants import NOTE_STATUS_PUBLISHED
        if user and user.is_authenticated:
            user_tags = NoteTag.objects.filter(note__user=user).values_list("tag_id", flat=True).distinct()
            from apps.social.models import Follow
            following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)
            qs = Note.objects.filter(
                Q(tags__in=list(user_tags)) | Q(user_id__in=list(following_ids)),
                status=NOTE_STATUS_PUBLISHED
            ).distinct().order_by("-created_at")
        else:
            hot_tags = Tag.objects.order_by("-hot_value")[:5]
            qs = Note.objects.filter(tags__in=list(hot_tags), status=NOTE_STATUS_PUBLISHED).order_by("-created_at")
        return qs
