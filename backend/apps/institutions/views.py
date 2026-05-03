from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAdminRole
from core.throttles import RegisterInstitutionThrottle
from .serializers import (
    InstitutionSerializer,
    InstitutionUpdateSerializer,
    InstitutionRegistrationSerializer,
    InstitutionVerifySerializer,
)
from .services import InstitutionService


class InstitutionRegisterView(APIView):
    """POST /api/institutions/register/ — public self-service signup."""

    permission_classes = []
    throttle_classes = [RegisterInstitutionThrottle]

    def post(self, request):
        serializer = InstitutionRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        data = InstitutionService.register(
            institution_name=d["institution_name"],
            admin_name=d["admin_name"],
            email=d["email"],
            password=d["password"],
        )
        return Response(data, status=status.HTTP_201_CREATED)


class InstitutionVerifyView(APIView):
    """POST /api/institutions/verify/ — activate institution via email token."""

    permission_classes = []

    def post(self, request):
        serializer = InstitutionVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            InstitutionService.verify_institution(serializer.validated_data["token"])
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Instituição verificada com sucesso. Pode agora fazer login."})


class InstitutionDetailView(APIView):
    """
    GET   /api/institutions/me/ — admin views their institution
    PATCH /api/institutions/me/ — admin updates their institution
    """

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        serializer = InstitutionSerializer(request.membership.institution)
        return Response(serializer.data)

    def patch(self, request):
        serializer = InstitutionUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = InstitutionService.update_institution(
            request.membership.institution,
            serializer.validated_data,
        )
        return Response(InstitutionSerializer(updated).data)
