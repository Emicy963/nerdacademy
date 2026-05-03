from django.urls import path
from .views import (
    LoginView, CookieTokenRefreshView, LogoutView, MeView, MembershipsView,
    ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView,
)

urlpatterns = [
    path("login/",                   LoginView.as_view(),               name="login"),
    path("refresh/",                 CookieTokenRefreshView.as_view(),  name="token-refresh"),
    path("logout/",                  LogoutView.as_view(),              name="logout"),
    path("me/",                      MeView.as_view(),                  name="me"),
    path("memberships/",             MembershipsView.as_view(),         name="memberships"),
    path("change-password/",         ChangePasswordView.as_view(),      name="change-password"),
    path("password-reset/",          PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/",  PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
