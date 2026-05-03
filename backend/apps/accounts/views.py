from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from core.throttles import LoginRateThrottle, PasswordResetRateThrottle
from .serializers import (
    UserMeSerializer, MembershipSerializer, ChangePasswordSerializer,
    UserUpdateMeSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
)
from .services import UserService


def _set_refresh_cookie(response, refresh_token: str) -> None:
    cfg = settings.REFRESH_TOKEN_COOKIE
    response.set_cookie(
        key=cfg["name"],
        value=refresh_token,
        max_age=cfg["max_age"],
        httponly=True,
        secure=cfg["secure"],
        samesite=cfg["samesite"],
        path=cfg["path"],
    )


def _clear_refresh_cookie(response) -> None:
    cfg = settings.REFRESH_TOKEN_COOKIE
    response.delete_cookie(cfg["name"], path=cfg["path"])


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = response.data.pop("refresh", None)
            if refresh:
                _set_refresh_cookie(response, refresh)
        return response


class CookieTokenRefreshView(APIView):
    """Reads the refresh token from the HttpOnly cookie instead of the request body."""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE["name"])
        if not refresh_token:
            return Response(
                {"detail": "Sessão expirada. Faça login novamente."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            response = Response(
                {"detail": "Sessão expirada. Faça login novamente."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            _clear_refresh_cookie(response)
            return response

        data = serializer.validated_data
        response = Response({"access": data["access"]})
        if "refresh" in data:
            _set_refresh_cookie(response, data["refresh"])
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = (
            request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE["name"])
            or request.data.get("refresh")
        )
        try:
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        _clear_refresh_cookie(response)
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateMeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserService.update_me(request.user, serializer.validated_data["email"])
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserMeSerializer(user).data)


class MembershipsView(APIView):
    """GET /api/auth/memberships/ — list all active memberships for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = (
            request.user.memberships
            .filter(is_active=True)
            .select_related("institution")
            .order_by("institution__name")
        )
        return Response(MembershipSerializer(memberships, many=True).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.change_password(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Password updated successfully."})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.request_password_reset(serializer.validated_data["email"])
        return Response(
            {"detail": "Se o email existir, um link de recuperação foi enviado."}
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.confirm_password_reset(
                uid_b64=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Senha redefinida com sucesso."})
