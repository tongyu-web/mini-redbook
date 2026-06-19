from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r"", views.NoteViewSet, basename="note")

urlpatterns = [
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("tags/<str:tag_id>/notes/", views.TagNoteListView.as_view(), name="tag-notes"),
    path("user/<str:user_id>/", views.UserNoteListView.as_view(), name="user-notes"),
    path("liked/", views.LikedNoteListView.as_view(), name="liked-notes"),
    path("drafts/manage/", views.DraftListView.as_view(), name="draft-manage"),
    path("drafts/manage/<str:pk>/", views.DraftListView.as_view(), name="draft-delete"),
    path("recycle/restore/<str:pk>/", views.NoteRestoreView.as_view(), name="note-restore"),
    path("recycle/hard-delete/<str:pk>/", views.NoteHardDeleteView.as_view(), name="note-hard-delete"),
    path("recycle/cleanup/", views.RecycleBinCleanupView.as_view(), name="recycle-cleanup"),
    path("<str:note_id>/comments/", views.CommentView.as_view(), name="comment-list"),
] + router.urls
