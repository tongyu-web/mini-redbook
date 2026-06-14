from django.urls import path
from . import views

urlpatterns = [
    path("follow/<str:user_id>/", views.FollowView.as_view(), name="toggle-follow"),
    path("notes/<str:note_id>/like/", views.LikeView.as_view(), name="toggle-like"),
    path("favorite-folders/", views.FavoriteFolderViewSet.as_view({"get": "list", "post": "create"}), name="folder-list"),
    path("favorite-folders/<str:pk>/", views.FavoriteFolderViewSet.as_view({"delete": "destroy"}), name="folder-detail"),
    path("favorites/all/", views.FavoriteAllView.as_view(), name="favorites-all"),
    path("favorites/<str:folder_id>/", views.FavoriteView.as_view(), name="favorite-list"),
    path("favorites/", views.FavoriteView.as_view(), name="favorite-add"),
]
