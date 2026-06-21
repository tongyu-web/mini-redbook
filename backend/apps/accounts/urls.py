from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/status/", views.ProfileStatusView.as_view(), name="profile-status"),
    path("profile/avatar/", views.AvatarUploadView.as_view(), name="avatar-upload"),
    path("profile/", views.ProfileView.as_view(), name="my-profile"),
    path("profile/<str:user_id>/", views.ProfileView.as_view(), name="user-profile"),
    path("password/change/", views.ChangePasswordView.as_view(), name="change-password"),
    path("email/bind/", views.BindEmailView.as_view(), name="bind-email"),
    path("email/send-code/", views.SendEmailCodeView.as_view(), name="send-email-code"),
    path("email/bind-with-code/", views.BindEmailWithCodeView.as_view(), name="bind-email-code"),
    path("email/unbind/", views.UnbindEmailView.as_view(), name="unbind-email"),
    path("privacy/", views.PrivacySettingsView.as_view(), name="privacy-settings"),
    path("cancel/", views.CancelAccountView.as_view(), name="cancel-account"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("<str:user_id>/followers/", views.FollowersListView.as_view(), name="followers"),
    path("<str:user_id>/following/", views.FollowingListView.as_view(), name="following"),
]
