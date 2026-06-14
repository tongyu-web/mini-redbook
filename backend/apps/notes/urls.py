from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r"", views.NoteViewSet, basename="note")

urlpatterns = [
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("user/<str:user_id>/", views.UserNoteListView.as_view(), name="user-notes"),
    path("liked/", views.LikedNoteListView.as_view(), name="liked-notes"),
    path("<str:note_id>/comments/", views.CommentView.as_view(), name="comment-list"),
] + router.urls
