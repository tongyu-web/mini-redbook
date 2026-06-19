from django.urls import path
from . import views

urlpatterns = [
    path("notifications/", views.NotificationViewSet.as_view({"get": "list"}), name="notification-list"),
    path("notifications/<str:pk>/", views.NotificationViewSet.as_view({"patch": "partial_update"}), name="notification-detail"),
    path("notifications/unread-count/", views.UnreadCountView.as_view(), name="unread-count"),
    path("notifications/read-all/", views.MarkAllReadView.as_view(), name="read-all"),
    path("conversations/", views.ConversationView.as_view(), name="conversation-list"),
    path("conversations/<str:user_id>/", views.DeleteConversationView.as_view(), name="conversation-delete"),
    path("messages/<str:user_id>/", views.MessageView.as_view(), name="message-list"),
    path("messages/", views.MessageView.as_view(), name="message-send"),
    path("block/<str:user_id>/", views.BlockContactView.as_view(), name="block-contact"),
]
