from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAdminRole
from .serializers import InstitutionSerializer, InstitutionUpdateSerializer
from .services import InstitutionService


class InstitutionDetailView(APIView):
    """
    GET   /api/institutions/me/ — admin views their institution
    PATCH /api/institutions/me/ — admin updates their institution
    """

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        serializer = InstitutionSerializer(request.user.institution)
        return Response(serializer.data)

    def patch(self, request):
        serializer = InstitutionUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = InstitutionService.update_institution(
            request.user.institution,
            serializer.validated_data,
        )
        return Response(InstitutionSerializer(updated).data)
