from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r"", views.NoteViewSet, basename="note")
# NoteViewSet: list(GET /notes/), create(POST), retrieve(GET /notes/{pk}/), update(PATCH /notes/{pk}/), destroy(DELETE /notes/{pk}/)

urlpatterns = [
    path("tags/", views.TagListView.as_view(), name="tag-list"),
    path("<str:note_id>/comments/", views.CommentView.as_view(), name="comment-list"),
] + router.urls
