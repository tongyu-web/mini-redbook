from django.db import models, transaction
from django.db.models import Q
from .models import SearchHistory, HotSearchTerm
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

        with transaction.atomic():
            term, created = HotSearchTerm.objects.get_or_create(
                keyword=keyword,
                defaults={"search_count": 1}
            )
            if not created:
                HotSearchTerm.objects.filter(pk=term.pk).update(search_count=models.F("search_count") + 1)

        from apps.notes.models import Note
        from apps.accounts.models import User
        from apps.notes.models import Tag

        if search_type == "note":
            qs = Note.objects.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword),
                status=NOTE_STATUS_PUBLISHED
            ).select_related("user").order_by("-created_at")
        elif search_type == "user":
            qs = User.objects.filter(
                Q(nickname__icontains=keyword) | Q(username__icontains=keyword),
                account_status=ACCOUNT_STATUS_NORMAL
            )
        elif search_type == "tag":
            qs = Tag.objects.filter(name__icontains=keyword).order_by("-hot_value")
        else:
            qs = Note.objects.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword),
                status=NOTE_STATUS_PUBLISHED
            ).select_related("user").order_by("-created_at")

        start = (page - 1) * page_size
        end = start + page_size
        total = qs.count()
        page_items = qs[start:end]

        if search_type == "note":
            from apps.notes.serializers import NoteListSerializer
            from django.http import HttpRequest
            fake_req = HttpRequest()
            fake_req.user = user if user and user.is_authenticated else type("AnonymousUser", (), {"is_authenticated": False})()
            fake_req.META = {"SERVER_NAME": "localhost", "SERVER_PORT": "8000", "HTTP_HOST": "localhost:8000", "wsgi.url_scheme": "http"}
            ser = NoteListSerializer(page_items, many=True, context={"request": fake_req})
            return {"count": total, "results": ser.data}
        elif search_type == "user":
            from apps.accounts.serializers import UserSimpleSerializer
            from django.http import HttpRequest
            fake_req = HttpRequest()
            fake_req.user = user if user and user.is_authenticated else type("AnonymousUser", (), {"is_authenticated": False})()
            fake_req.META = {"SERVER_NAME": "localhost", "SERVER_PORT": "8000", "HTTP_HOST": "localhost:8000", "wsgi.url_scheme": "http"}
            ser = UserSimpleSerializer(page_items, many=True, context={"request": fake_req})
            return {"count": total, "results": ser.data}
        elif search_type == "tag":
            data = [{"name": t.name, "hot_value": t.hot_value, "note_count": t.note_count} for t in page_items]
            return {"count": total, "results": data}
        return {"count": 0, "results": []}

    @staticmethod
    def suggest(prefix):
        from apps.notes.models import Tag
        return list(Tag.objects.filter(name__istartswith=prefix).order_by("-hot_value")[:10].values("name", "hot_value"))

    @staticmethod
    def hot_tags():
        from apps.notes.models import Tag
        return list(Tag.objects.order_by("-hot_value")[:20].values("name", "hot_value", "note_count"))

    @staticmethod
    def hot_search_terms(limit=20):
        qs = HotSearchTerm.objects.order_by("-search_count")[:limit]
        return list(qs.values("keyword", "search_count", "updated_at"))

    @staticmethod
    def recommend(user):
        from apps.notes.models import Note
        from config.constants import NOTE_STATUS_PUBLISHED
        qs = Note.objects.filter(status=NOTE_STATUS_PUBLISHED).order_by("-created_at")
        return qs
