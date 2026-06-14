from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/", views.ProfileView.as_view(), name="my-profile"),
    path("profile/<str:user_id>/", views.ProfileView.as_view(), name="user-profile"),
    path("profile/avatar/", views.AvatarUploadView.as_view(), name="avatar-upload"),
    path("profile/status/", views.ProfileStatusView.as_view(), name="profile-status"),
    path("<str:user_id>/followers/", views.FollowersListView.as_view(), name="followers"),
    path("<str:user_id>/following/", views.FollowingListView.as_view(), name="following"),
]
