from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import PaginatedListMixin
from core.permissions import IsAdminRole, IsTrainerRole
from .serializers import (
    TrainerSerializer,
    TrainerCreateSerializer,
    TrainerUpdateSerializer,
    TrainerPublicSerializer,
)
from .services import TrainerService


class TrainerListCreateView(PaginatedListMixin, APIView):
    """
    GET  /api/trainers/ — list trainers (admin only)
    POST /api/trainers/ — create trainer (admin only)
    """

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        search = request.query_params.get("search")
        is_active = request.query_params.get("is_active")

        if is_active is not None:
            is_active = is_active.lower() == "true"

        trainers = TrainerService.list_trainers(
            institution=request.user.institution,
            search=search,
            is_active=is_active,
        )
        return self.paginate(request, trainers, TrainerSerializer)

    def post(self, request):
        serializer = TrainerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trainer = TrainerService.create_trainer(
            institution=request.user.institution,
            **serializer.validated_data,
        )
        return Response(TrainerSerializer(trainer).data, status=status.HTTP_201_CREATED)


class TrainerDetailView(APIView):
    """
    GET    /api/trainers/{id}/ — detail (admin only)
    PATCH  /api/trainers/{id}/ — update (admin only)
    DELETE /api/trainers/{id}/ — deactivate (admin only)
    """

    permission_classes = [IsAuthenticated, IsAdminRole]

    def _get_trainer(self, request, trainer_id):
        return TrainerService.get_trainer(
            trainer_id=trainer_id,
            institution=request.user.institution,
        )

    def get(self, request, trainer_id):
        trainer = self._get_trainer(request, trainer_id)
        return Response(TrainerSerializer(trainer).data)

    def patch(self, request, trainer_id):
        trainer = self._get_trainer(request, trainer_id)
        serializer = TrainerUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = TrainerService.update_trainer(trainer, serializer.validated_data)
        return Response(TrainerSerializer(updated).data)

    def delete(self, request, trainer_id):
        trainer = self._get_trainer(request, trainer_id)
        TrainerService.deactivate_trainer(trainer)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrainerClassesView(APIView):
    """
    GET /api/trainers/{id}/classes/ — list classes for a trainer.
    Admins see any trainer's classes; trainers see only their own.
    """

    permission_classes = [IsAuthenticated, IsTrainerRole]

    def get(self, request, trainer_id):
        trainer = TrainerService.get_trainer(
            trainer_id=trainer_id,
            institution=request.user.institution,
        )
        # Trainers can only see their own classes
        if request.user.is_trainer:
            try:
                own_trainer = TrainerService.get_trainer_by_user(request.user)
            except Exception:
                return Response([], status=status.HTTP_200_OK)
            if str(own_trainer.id) != str(trainer_id):
                return Response(
                    {"detail": "You can only view your own classes."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        from apps.classes.serializers import ClassSummarySerializer

        classes = TrainerService.get_trainer_classes(trainer)
        serializer = ClassSummarySerializer(classes, many=True)
        return Response(serializer.data)


class MyTrainerProfileView(APIView):
    """
    GET /api/trainers/me/ — trainer views their own profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        trainer = TrainerService.get_trainer_by_user(request.user)
        return Response(TrainerPublicSerializer(trainer).data)
